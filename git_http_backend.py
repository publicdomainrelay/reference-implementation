import os
import sys
import json
import atexit
import asyncio
import base64
import pprint
import warnings
from aiohttp import web
from pathlib import Path
from io import BytesIO
from typing import Optional
import zipfile
import hashlib
import configparser
import subprocess
import argparse

from pydantic import BaseModel, Field
from atproto import Client, models
import keyring
import snoop

# Helper scripts for APIs not available to Python client, etc.
# TODO importlib.resources once packaged
ATPROTO_UPDATE_PROFILE_JS_PATH = Path(__file__).parent.resolve().joinpath("update_profile.js")

# TODO Make hash_alg configurable
hash_alg = 'sha384'

# TODO DEBUG REMOVE
os.environ["HOME"] = str(Path(__file__).parent.resolve())

parser = argparse.ArgumentParser(prog='atproto-git', usage='%(prog)s [options]')
parser.add_argument('--repos-directory', dest="repos_directory", help='directory for local copies of git repos')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(str(Path("~", ".gitconfig").expanduser()))

atproto_handle = config["user"]["atproto"]
atproto_handle_username = atproto_handle.split(".")[0]
atproto_base_url = "https://" + ".".join(atproto_handle.split(".")[1:])
atproto_email = config["user"]["email"]
atproto_password = keyring.get_password(
    atproto_email,
    ".".join(["password", atproto_handle]),
)

class CacheATProtoIndex(BaseModel):
    owner_profile: Optional[models.app.bsky.actor.defs.ProfileViewDetailed] = None
    root: Optional[models.base.RecordModelBase] = None
    entries: dict[str, 'CacheATProtoIndex'] = Field(
        default_factory=lambda: {},
    )

atproto_index = CacheATProtoIndex()
atproto_index_path = Path("~", ".cache", "atproto_vcs_git_cache.json").expanduser()
atproto_index_path.parent.mkdir(parents=True, exist_ok=True)
atexit.register(
    lambda: atproto_index_path.write_text(
        atproto_index.model_dump_json(),
    )
)
if atproto_index_path.exists():
    atproto_index = CacheATProtoIndex.model_validate_json(atproto_index_path.read_text())

client = Client(
    base_url=atproto_base_url,
)
client.login(
    atproto_handle,
    atproto_password,
)

if atproto_index.owner_profile is None:
    atproto_index.owner_profile = client.get_profile(atproto_handle)
atproto_index.root = atproto_index.owner_profile.pinned_post

def update_profile(client, pinned_post):
    # TODO Use Python client APIs once available
    global atproto_base_url
    global atproto_handle
    global atproto_password
    env = {
        **os.environ,
        **{
            "ATPROTO_BASE_URL": atproto_base_url,
            "ATPROTO_HANDLE": atproto_handle,
            "ATPROTO_PASSWORD": atproto_password,
            "ATPROTO_PINNED_POST_URI": atproto_index.root.uri,
            "ATPROTO_PINNED_POST_CID": atproto_index.root.cid,
        },
    }
    cmd = [
        "deno",
        "--allow-env",
        "--allow-net",
        str(ATPROTO_UPDATE_PROFILE_JS_PATH.name),
    ]
    proc_result = subprocess.run(
        cmd,
        cwd=str(ATPROTO_UPDATE_PROFILE_JS_PATH.parent.resolve()),
        env=env,
    )
    proc_result.check_returncode()

if atproto_index.root is None:
    atproto_index.root = client.send_post(text="index")
    update_profile(
        client,
        pinned_post=atproto_index.root,
    )

def atproto_index_read(client, index, depth: int = 100):
    for index_type, index_entry in client.get_post_thread(
        index.root.uri,
        depth=depth,
    ):
        snoop.pp(index_type, index_entry)
        if index_type == 'thread':
            if index_entry.post.author.did == index.owner_profile.did:
                # pprint.pprint(json.loads(index_entry.model_dump_json()))
                for reply in index_entry.replies:
                    if reply.post.author.did == index.owner_profile.did:
                        sub_index = index.__class__(
                            owner_profile=index.owner_profile,
                            root=models.base.RecordModelBase(
                                uri=reply.post.uri,
                                cid=reply.post.cid,
                            )
                        )
                        atproto_index_read(client, sub_index, depth=depth)
                        if reply.post.record.text in index.entries:
                            index.entries[reply.post.record.text].entries.update(
                                sub_index.entries,
                            )
                        else:
                            index.entries[reply.post.record.text] = sub_index
        elif index_type == 'threadgate':
            pass
        else:
            warnings.warn(f"Unkown get_post_thread().index_type: {index_type!r}: {pprint.pformat(index_entry)}")

def atproto_index_create(index, index_entry_key, data_as_image: bytes = None, data_as_image_hash: str = None):
    if index_entry_key in index.entries:
        return
    parent = models.create_strong_ref(index.root)
    root = models.create_strong_ref(index.root)
    method = client.send_post
    kwargs = {}
    if data_as_image is not None:
        method = client.send_image
        kwargs["image"] = data_as_image
        if data_as_image_hash is not None:
            kwargs["image_alt"] = data_as_image_hash
    post = method(
        text=index_entry_key,
        reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent, root=root),
        **kwargs,
    )
    index.entries[index_entry_key] = index.__class__(
        owner_profile=index.owner_profile,
        root=models.base.RecordModelBase(
            uri=post.uri,
            cid=post.cid,
        )
    )

atproto_index_read(client, atproto_index)
atproto_index_create(atproto_index, "vcs")
atproto_index_create(atproto_index.entries["vcs"], "git")
atproto_index_read(client, atproto_index.entries["vcs"].entries["git"])

# Configuration
GIT_PROJECT_ROOT = args.repos_directory
GIT_HTTP_EXPORT_ALL = "1"

# Ensure the project root exists
os.makedirs(GIT_PROJECT_ROOT, exist_ok=True)

@snoop
def snoop_repos():
    for repo_name in atproto_index.entries["vcs"].entries["git"].entries:
        snoop.pp(repo_name)

snoop_repos()

# Utility to list all internal files in a Git repository
def list_git_internal_files(repo_path):
    files = []
    git_dir = Path(repo_path)
    for file in git_dir.rglob("*"):
        if file.is_file():
            yield file

# Create a zip archive containing the internal files
def create_zip_of_files(files):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            arcname = str(file.relative_to(file.anchor))
            zipf.write(file, arcname=arcname)
    zip_buffer.seek(0)
    return zip_buffer.read()

# Create a PNG image that also contains the zip archive
def create_png_with_zip(zip_data):
    # Create a minimal PNG header
    png_header = (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\r'     # IHDR chunk length
        b'IHDR'               # IHDR chunk type
        b'\x00\x00\x00\x01'   # Width: 1
        b'\x00\x00\x00\x01'   # Height: 1
        b'\x08'               # Bit depth: 8
        b'\x02'               # Color type: Truecolor
        b'\x00'               # Compression method
        b'\x00'               # Filter method
        b'\x00'               # Interlace method
        b'\x90wS\xde'         # CRC
        b'\x00\x00\x00\x0a'   # IDAT chunk length
        b'IDAT'               # IDAT chunk type
        b'\x78\x9c\x63\x60\x00\x00\x00\x02\x00\x01'  # Compressed data
        b'\x02\x7e\xe5\x45'   # CRC
        b'\x00\x00\x00\x00'   # IEND chunk length
        b'IEND'               # IEND chunk type
        b'\xaeB`\x82'         # CRC
    )
    # Combine the PNG header and the zip data
    png_zip_data = png_header + zip_data
    return png_zip_data

# Handle Git HTTP Backend requests
async def handle_git_backend_request(request):
    global hash_alg

    path_info = request.match_info.get("path", "")
    env = {
        "GIT_PROJECT_ROOT": GIT_PROJECT_ROOT,
        "GIT_HTTP_EXPORT_ALL": GIT_HTTP_EXPORT_ALL,
        "PATH_INFO": f"/{path_info}",
        "REMOTE_USER": request.remote or "",
        "REMOTE_ADDR": request.transport.get_extra_info("peername")[0],
        "REQUEST_METHOD": request.method,
        "QUERY_STRING": request.query_string,
        "CONTENT_TYPE": request.headers.get("Content-Type", ""),
    }

    # Copy relevant HTTP headers to environment variables
    for header in ("Content-Type", "User-Agent", "Accept-Encoding", "Pragma"):
        header_value = request.headers.get(header)
        if header_value:
            env["HTTP_" + header.upper().replace("-", "_")] = header_value

    # Prepare the subprocess to run git http-backend
    proc = await asyncio.create_subprocess_exec(
        "git", "http-backend",
        env=env,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=sys.stderr,  # Output stderr to the server's stderr
    )

    # Forward the request body to git http-backend
    async def write_to_git(stdin):
        try:
            async for chunk in request.content.iter_chunked(4096):
                stdin.write(chunk)
            await stdin.drain()
        except Exception as e:
            print(f"Error writing to git http-backend: {e}", file=sys.stderr)
        finally:
            if not stdin.is_closing():
                stdin.close()

    # Read the response from git http-backend and send it back to the client
    async def read_from_git(stdout, response):
        headers = {}
        headers_received = False
        buffer = b""

        while True:
            chunk = await stdout.read(4096)
            if not chunk:
                break
            buffer += chunk
            if not headers_received:
                header_end = buffer.find(b'\r\n\r\n')
                if header_end != -1:
                    header_data = buffer[:header_end].decode('utf-8', errors='replace')
                    body = buffer[header_end+4:]
                    # Parse headers
                    for line in header_data.split('\r\n'):
                        if line:
                            key, value = line.split(':', 1)
                            headers[key.strip()] = value.strip()
                    # Send headers to the client
                    for key, value in headers.items():
                        response.headers[key] = value
                    await response.prepare(request)
                    await response.write(body)
                    headers_received = True
                    buffer = b""
            else:
                # Send body to the client
                await response.write(chunk)
        if not headers_received:
            # If no headers were sent, send what we have
            await response.prepare(request)
            await response.write(buffer)
        await response.write_eof()

    # Create a StreamResponse to send data back to the client
    response = web.StreamResponse()

    # Run the read and write tasks concurrently
    await asyncio.gather(
        write_to_git(proc.stdin),
        read_from_git(proc.stdout, response),
    )

    # Wait for the subprocess to finish
    await proc.wait()

    # Handle push events (git-receive-pack)
    print(f"path_info: {path_info}")
    if path_info.endswith("git-receive-pack"):
        repo_name = Path(path_info).parent.name
        repo_path = Path(GIT_PROJECT_ROOT, repo_name)
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        atproto_index_create(atproto_index.entries["vcs"].entries["git"], repo_name)
        for internal_file in list_git_internal_files(repo_path):
            repo_file_path = str(internal_file.relative_to(repo_path))
            print(f"Updated internal file in {repo_name}: {repo_file_path}")

            # Create zip archive of internal files
            zip_data = create_zip_of_files([internal_file])

            # Create PNG with embedded zip
            png_zip_data = create_png_with_zip(zip_data)

            # Base64 encode the PNG data
            # encoded_data = base64.b64encode(png_zip_data).decode('utf-8')

            # Output the data URL
            # data_url = f"data:image/png;base64,{encoded_data}"
            # print(data_url)
            # atproto_index_create(atproto_index.entries["vcs"]["git"], data_url)
            hash_instance = hashlib.new(hash_alg)
            hash_instance.update(internal_file.read_bytes())
            data_as_image_hash = hash_instance.hexdigest()
            atproto_index_create(
                atproto_index.entries["vcs"].entries["git"].entries[repo_name],
                repo_file_path,
                data_as_image=png_zip_data,
                data_as_image_hash=f"{hash_alg}:{data_as_image_hash}",
            )

    return response

# Set up the application
app = web.Application()
app.router.add_route("*", "/{path:.*}", handle_git_backend_request)

if __name__ == "__main__":
    # Ensure there is a bare Git repository for testing
    test_repo_path = os.path.join(GIT_PROJECT_ROOT, "my-repo.git")
    if not os.path.exists(test_repo_path):
        os.makedirs(GIT_PROJECT_ROOT, exist_ok=True)
        os.system(f"git init --bare {test_repo_path}")
        os.system(f"rm -rf {test_repo_path}/hooks/")
        print(f"Initialized bare repository at {test_repo_path}")

    # Start the server
    web.run_app(app, host="0.0.0.0", port=8080)
