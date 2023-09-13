import argparse
import logging
import pathlib
import re
import shutil
import subprocess
import time
from getpass import getpass, getuser


logger = logging.getLogger("setup-image")


def set_password() -> str:
    return getpass(f"Please enter password for user {args.username}: ")


def mount_image(image_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    subprocess.check_output(["udisksctl", "loop-setup", "-f", image_path])

    bootfs_path = pathlib.Path(f"/run/media/{getuser()}/bootfs")
    rootfs_path = pathlib.Path(f"/run/media/{getuser()}/rootfs")

    while not bootfs_path.exists() or not rootfs_path.exists():
        time.sleep(0.1)

    return bootfs_path, rootfs_path


def enable_ssh(bootfs_path: pathlib.Path) -> None:
    (bootfs_path / "ssh").touch()


def setup_user(bootfs_path: pathlib.Path) -> None:
    (bootfs_path / "userconf.txt").write_text(
        f"{args.username}:{generate_encrypted_password(args.password)}"
    )


def generate_encrypted_password(password):
    result = subprocess.check_output(["openssl", "passwd", "-6", password])
    return result.decode("utf-8").strip()


def set_authorized_keys(rootfs_path: pathlib.Path, path_to_pub_key: pathlib.Path):
    pubkey = path_to_pub_key.read_text()
    ssh_folder = rootfs_path / "home/pi/.ssh"
    ssh_folder.mkdir(mode=0o700, exist_ok=True)

    authorized_keys = ssh_folder / "authorized_keys"
    if authorized_keys.exists() and pubkey in authorized_keys.read_text():
        logger.info("Public key already exists in authorized_keys")
        return

    with open(authorized_keys, "a") as f:
        print(pubkey, file=f)


def unmount(path):
    n_tries = 10
    for _ in range(n_tries):
        try:
            subprocess.check_output(["umount", path])
        except subprocess.CalledProcessError:
            time.sleep(1)
        else:
            break
    else:
        raise RuntimeError(f"Could not unmount {path}")


logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    description="""
Mount raspbian image, enable ssh and set default username and password
"""
)
parser.add_argument("image_path", help="Path to image")
parser.add_argument("--username", default="pi", help="Username")
parser.add_argument("--password", help="Password for user")
parser.add_argument(
    "--pub-key", type=pathlib.Path, help="Path to public key for ssh authentication"
)
args = parser.parse_args()


if not args.password:
    args.password = set_password()

try:
    bootfs_path, rootfs_path = mount_image(args.image_path)
    enable_ssh(bootfs_path)
    setup_user(bootfs_path)
    if args.pub_key:
        set_authorized_keys(rootfs_path, args.pub_key)

finally:
    for path in (bootfs_path, rootfs_path):
        unmount(path)
