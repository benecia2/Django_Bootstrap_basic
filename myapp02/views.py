from django.shortcuts import render, redirect
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from myapp02.models import Board, Comment
from .form import UserForm
from django.db.models import Q
import math
from django.core.paginator import Paginator


# Create your views here.

# write_form (추가폼)
def write_form(request):
    return render(request, 'board/insert.html')

# 업로드 파일위치
UPLOAD_DIR = 'D:/DJANGOWORK/upload/'


# signup 회원가입
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect('/')
        else:
            print("signup POST un_valid")
    else:
        form = UserForm()
        
    return render(request, 'common/signup.html',{'form':form})

# insert 추가하기
@csrf_exempt
def insert(request):
    fname = ''
    fsize = 0
    if 'file' in request.FILES :
        file = request.FILES['file']
        fsize = file.size
        fname = file.name
        fp = open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    board = Board(writer = request.POST['writer'],
                    title = request.POST['title'],
                    content = request.POST['content'],
                    filename = fname,
                    filesize = fsize
                    )
    board.save()
    return redirect("/list")

# list(검색추가)
def list(request):
    page = request.GET.get('page',1)
    word = request.GET.get('word','')
    field = request.GET.get('field', 'title')
    # count
    if field == 'all':
        boardCount = Board.objects.filter(Q(writer__contains=word)|
                                        Q(title__contains=word)|
                                        Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(Q(writer__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(Q(title__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(Q(content__contains=word)).count()
    else:
        boardCount = Board.objects.all().count

    # page
    pageSize = 5
    blockPage = 3
    currentPage = int(page)
    # 123[다음]    [이전]456[다음]      [이전]7(89) 
    totPage = math.ceil(boardCount/pageSize) # 총 페이지 수(7)
    startPage = math.floor((currentPage-1)/blockPage)*blockPage+1
    endPage = startPage+blockPage-1 #( 현재 페이지가 7이라면 )
    if  endPage > totPage :
        endPage = totPage

    start = (currentPage-1)*pageSize

    # 내용
    if field == 'all':
        boardList = Board.objects.filter(Q(writer__contains=word)|
                                        Q(title__contains=word)|
                                        Q(content__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(Q(writer__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(Q(title__contains=word)).order_by('-id')[start:start+pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(Q(content__contains=word)).order_by('-id')[start:start+pageSize]
    else:
        boardList = Board.objects.all().order_by('-id')[start:start+pageSize]


    context = {'boardList' : boardList,
                'boardCount' : boardCount,
                'field' : field,
                'word' : word,
                'startPage' : startPage,
                'blockPage' : blockPage,
                'endPage' : endPage,
                'totPage': totPage,
                'range': range(startPage,endPage+1),
                'currentPage' : currentPage}
    return render(request, 'board/list.html', context)


# list_page
def list_page(request):
    page = request.GET.get('page',1)
    word = request.GET.get('word','')

    boardCount = Board.objects.filter(
                                    Q(writer__contains = word)|
                                    Q(title__contains = word)|
                                    Q(content__contains = word)).count()
    
    boardList = Board.objects.filter(
                                    Q(writer__contains = word)|
                                    Q(title__contains = word)|
                                    Q(content__contains = word)).order_by('-id')

    # 페이징 처리
    pageSize = 5

    paginator = Paginator(boardList,pageSize)
    page_obj = paginator.get_page(page)
    print('page_obj:',page_obj)

    context = {
        'boardCount':boardCount,
        'page_list' :page_obj,
        'word':word
    }

    return render(request, 'board/list_page.html',context)


# detail : 상세보기     /detail/1" ==> detail/<int:board_id>
def detail(request, board_id):
    # print('board_id : ',board_id)
    board = Board.objects.get(id=board_id)
    # 조회수 1증가
    board.hit_up()
    board.save()
    # comment list
    commentList = Comment.objects.filter(board_id = board_id).order_by('-id')
    commentCnt = Comment.objects.filter(board_id=board_id).count
    print('commentList sql : ', commentList.query)
    return render(request, 'board/detail.html',{'board':board,  'commentList': commentList})


# delete : 삭제
def delete(request,board_id):
    Board.objects.get(id=board_id).delete()
    return redirect("/list/")

# download_count
def download_count(request):
    id = request.GET['id']
    print('id : ',id)
    board = Board.objects.get(id = id)
    board.down_up()   # 다운로드 수 증가
    board.save()
    count = board.down    # 다운로드 수
    print('count : ', count)
    return JsonResponse({'id' : id, 'count': count})

# download
def download(request):
    id = request.GET['id']
    board = Board.objects.get(id = id)
    path = UPLOAD_DIR + board.filename
    # filename = urllib.parse.quote(board.filename)
    filename = board.filename

    with open(path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition']="attachment;filename*=UTF-8''{0}".format(filename)

        return response
    

# update_form
def update_form(request, board_id):
    board = Board.objects.get(id=board_id)
    context = {'board':board}
    return render(request, 'board/update.html', context)

# update
@csrf_exempt
def update(request):
    id = request.POST['id']
    board = Board.objects.get(id = id)
    fname = board.filename
    fsize = board.filesize
    # file 수정
    if 'file' in request.FILES :
        file = request.FILES['file']
        fsize = file.size
        fname = file.name
        fp = open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    board_update = Board(id,
                writer = request.POST['writer'],
                title = request.POST['title'],
                content = request.POST['content'],
                filename = fname,
                filesize = fsize
               )
    board_update.save()
    return redirect("/list")


# comment_insert
@csrf_exempt
def comment_insert(request):
    id = request.POST['id']
    cboard = Comment(board_id = id, writer = '홍길동', content = request.POST['content'])

    cboard.save()

    # return redirect("detail_id?id="+id)
    return redirect("/detail/"+id)