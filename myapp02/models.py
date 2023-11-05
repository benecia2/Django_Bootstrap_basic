from django.db import models
from datetime import datetime

# Create your models here.

class Board(models.Model):
    id = models.AutoField(primary_key=True) # id 안하면 자동으로 생성
    writer = models.CharField(null=False, max_length=50)
    title = models.CharField(null=False, max_length=200)
    content = models.TextField(null=False)
    hit = models.IntegerField(default=0)
    post_date = models.DateTimeField(default=datetime.now, blank=True)
    filename = models.CharField(null=True, blank=True, default='', max_length=50)
    filesize = models.IntegerField(default=0)
    down = models.ImageField(default=0)

    # 조회수
    def hit_up(self):
        self.hit += 1

    # 다운로드 횟수
    def down_up(self):
        self.down += 1



# 댓글
class Comment(models.Model):
    id = models.AutoField(primary_key=True) # id 안하면 자동으로 생성
    board_id = models.IntegerField(null=False)
    # board = models.ForeignKey(Board,on_delete=models.CASCADE)  <- id랑 board_id 대신에 활용가능
    writer = models.CharField(null=False, max_length=50)
    content = models.TextField(null=False)
    post_date = models.DateTimeField(default=datetime.now, blank=True)