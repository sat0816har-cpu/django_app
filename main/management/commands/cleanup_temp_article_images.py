import os
import time

from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "7日以上経過した記事本文画像の一時ファイルを削除します"

    def handle(self, *args, **options):

        temp_root = Path(settings.ARTICLE_TEMP_ROOT)

        if not temp_root.exists():
            self.stdout.write("一時画像フォルダはありません。")
            return

        # 7日間（秒）
        retention_seconds = 7 * 24 * 60 * 60

        now = time.time()
        deleted_count = 0

        for file_path in temp_root.rglob("*"):

            if not file_path.is_file():
                continue

            file_age = now - file_path.stat().st_mtime

            if file_age >= retention_seconds:
                file_path.unlink()
                deleted_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"一時画像を {deleted_count} 件削除しました。"
            )
        )
