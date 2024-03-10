"""File Manager."""

import os
import uuid
import shutil
import filetype
import aiofiles
import aiofiles.os
from time import time
from PIL import Image, ExifTags
from types import SimpleNamespace
# import io
# from app.helpers.fernet_helper import FernetHelper
from app.logger import get_log

AIOFILES_CHUNK_SIZE = 1024

log = get_log()


class FileManager:
    """File Manager."""

    # @staticmethod
    # def path_exists(path: str) -> bool:
    #     """Check if path exists."""
    #     return os.path.exists(path)

    # @staticmethod
    # def path_empty(path: str) -> bool:
    #     """Check if directory contains files."""
    #     return len(os.listdir(path)) == 0

    # @staticmethod
    # def path_create(path: str) -> None:
    #     """Create a new directory."""
    #     os.mkdir(path)
    #     log.debug("Create a new directory, path=%s." % path)

    # @staticmethod
    # def path_delete(path: str) -> None:
    #     """Delete path."""
    #     os.rmdir(path)
    #     log.debug("Delete path, path=%s." % path)

    # @staticmethod
    # async def path_truncate(path: str) -> None:
    #     """Delete all files and subdirectories in path."""
    #     for filename in os.listdir(path):
    #         file_path = os.path.join(path, filename)
    #         if os.path.isfile(file_path) or os.path.islink(file_path):
    #             os.unlink(file_path)
    #         elif os.path.isdir(file_path):
    #             shutil.rmtree(file_path)
    #     log.debug('Truncate directory, path=%s.' % path)

    # @staticmethod
    # def uuid() -> str:
    #     """Generate uuid."""
    #     return str(uuid.uuid4())

    # @staticmethod
    # def file_path(path: str) -> str:
    #     """Get absolute path to file directory."""
    #     return os.path.dirname(os.path.abspath(path))

    @staticmethod
    def get_filename(path: str) -> str:
        """Get file name without extension."""
        filename, _ = os.path.splitext(path)
        return filename

    @staticmethod
    def get_extension(path: str) -> str:
        """Get file extension."""
        _, ext = os.path.splitext(path)
        return ext

    @staticmethod
    def get_mimetype(path: str) -> str:
        """Get file mimetype."""
        kind = filetype.guess(path)
        return kind.mime if kind else None

    @staticmethod
    def get_filesize(path: str) -> int:
        """Get file size."""
        return os.path.getsize(path)
    
    # def get_meta(path: str):
    #     """Get image data."""
    #     im = Image.open(path)
    #     meta = SimpleNamespace()
    #     meta.bits = im.bits if hasattr(im, "bits") else None
    #     meta.format = im.format
    #     meta.size = im.size
    #     meta.mode = im.mode
    #     return meta

    def get_metadata(im: Image):
        """Get image metadata."""
        metadata = im._getexif()
        return {ExifTags.TAGS[k]: v for k, v in im._getexif().items() if k in ExifTags.TAGS} if metadata else {}

    # @staticmethod
    # def file_date(path: str) -> int:
    #     """Get file time in UNIX timestamp."""
    #     return int(os.stat(path).st_mtime)

    # @staticmethod
    # async def file_exists(path: str) -> bool:
    #     """Check if file exists."""
    #     return os.path.isfile(path)

    # @staticmethod
    # async def files_list(path: str) -> list:
    #     """Get files list in directory exclude filenames started with a dot."""
    #     files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith('.')]
    #     return sorted(files)

    @staticmethod
    async def file_copy(src_path: str, dst_dir: str) -> None:
        """Copy file."""
        dst_filename = os.path.join(str(uuid.uuid4()) + FileManager.get_extension(src_path))
        dst_path = os.path.join(dst_dir, dst_filename)

        # create file objects for the source and destination
        handle_src = await aiofiles.open(src_path, mode="r")
        handle_dst = await aiofiles.open(dst_path, mode="w")

        # get the number of bytes for the source
        stat_src = await aiofiles.os.stat(src_path)
        n_bytes = stat_src.st_size

        # get the file descriptors for the source and destination files
        fd_src = handle_src.fileno()
        fd_dst = handle_dst.fileno()

        await aiofiles.os.sendfile(fd_dst, fd_src, 0, n_bytes)
        return dst_filename

        # shutil.copyfile(src_path, dst_path)
        # log.debug('Copy file, src_path=%s, dst_path=%s' % (src_path, dst_path))

    # @staticmethod
    # async def file_move(src_path: str, dst_path: str) -> None:
    #     """Move/rename file."""
    #     os.rename(src_path, dst_path)
    #     log.debug('Move or rename file, src_path=%s, dst_path=%s' % (src_path, dst_path))

    # @staticmethod
    # async def cmd_exec(cmd: str) -> None:
    #     """Execute command."""
    #     os.system(cmd)
    #     log.debug('Execute command, cmd=%s' % cmd)

    @staticmethod
    async def file_upload(file: object, dst_dir: str) -> str:
        """Asynchronously upload a file under a unique filename and return the filename."""
        filename = os.path.join(str(uuid.uuid4()) + FileManager.get_extension(file.filename))
        path = os.path.join(dst_dir, filename)

        async with aiofiles.open(path, "wb") as fn:
            while content := await file.read(AIOFILES_CHUNK_SIZE):
                await fn.write(content)

        return filename

    @staticmethod
    async def file_delete(path: str) -> None:
        """Delete a file."""
        if await aiofiles.os.path.isfile(path):
            await aiofiles.os.unlink(path)

    # @staticmethod
    # def file_encrypt(base_path: str, filename: str, encryption_key: bytes) -> str:
    #     """Encrypt file and return filename."""
    #     file_ext = self.file_ext(filename)
    #     new_filename = filename.replace(file_ext, '')
    #     path = self.path_join(base_path, new_filename)
    #     self.file_move(self.path_join(base_path, filename), path)
    #     FernetHelper(encryption_key).encrypt_file(path)
    #     log.debug('File encrypted. Path=%s.' % path)
    #     return new_filename

    # @staticmethod
    # def file_decrypt(path: str, encryption_key: bytes) -> bytes:
    #     """Decrypt file and return bytes stream."""
    #     decrypted_file = io.BytesIO(FernetHelper(encryption_key).decrypt_file(path))
    #     log.debug('File decrypted. Path=%s.' % path)
    #     return decrypted_file
