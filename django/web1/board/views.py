# 파일명: board/views.py 
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
# byte 배열을 base64(이미지를 사용해줄 수 있게 만들어주는 포맷)로 변경함.
from base64 import b64encode
import pandas as pd
from .models import Table2 #models.py 파일의 Table2클래스, 모델 사용 위해 가져옴
from .models import Table1 #models.py 파일의 Table1클래스, 모델 사용 위해 가져옴



cursor = connection.cursor() # sql문 수행 위한 cursor 객체

# Create your views here. 

#TABLE1 관련 

@csrf_exempt
def dataframe(request):
    if request.method == 'GET':
        df = pd.read_sql(
            ''' 
            SELECT NO,TITLE, WRITER,HIT, REGDATE
            FROM BOARD_TABLE1
            ''', 
            con = connection

        )
        print(df)
        print(type(df["NO"]))
        return render(request, 'board/dataframe.html', {"df":df.to_html(classes ='table')}) # html파일에 표 형태로 df전달
        # df.to_html(classes = "클래스명") 하면 디자인 적용됨 


@csrf_exempt
def write(request):
    if request.method == 'GET':
        return render(request, 'board/write.html')
    
    elif request.method == 'POST':
        

        tmp = None
        if 'img' in request.FILES: # 이미지가 있으면 읽어들이고
            img = request.FILES['img']
            tmp = img.read()

        arr = [
            request.POST['title'],
            request.POST['content'],
            request.POST['writer'],
            tmp # 이미지를 byte[]로 변경(2진수 형태로)
        ]
        # print(arr)

        try :

                sql = ''' INSERT INTO BOARD_TABLE1(TITLE, CONTENT, WRITER, IMG, HIT, REGDATE)
                    VALUES(%s, %s, %s, %s, 234, SYSDATE)
                '''
        
                cursor.execute(sql, arr)

        except Exception as e:
            print(e)
    
        return redirect('/board/list') # <a href> 와 같음

 
@csrf_exempt
def list(request):
    if request.method == 'GET':
        request.session['hit'] = 1 #세션에 hit = 1 
        sql = '''
            SELECT NO, TITLE, CONTENT, WRITER, HIT, TO_CHAR(REGDATE, 'YYYY-MM-DD HH:MI:SS') 
            FROM BOARD_TABLE1
            ORDER BY NO DESC
        '''
        cursor.execute(sql)
        data = cursor.fetchall()
        print(type(data))
        print(data) 
        return render(request, 'board/list.html', {'abc':data})

# 127.0.0.1:8000/board/content?no=34
# 127.0.0.1:8000/board/content      ?no=0 >>오류발생 

@csrf_exempt
def content(request):
    if request.method == 'GET':
        no = request.GET.get('no',0) # 위에서 표기한 오류 해결 가능 
        if no == 0:
            return redirect("/board/list") 
        
        # 새로고침로인한 조회수 증가를 방지하기 위한 솔루션
        if request.session['hit'] == 1:  
            sql = '''
                UPDATE BOARD_TABLE1 SET HIT = HIT+1
                WHERE NO = %s
            '''
            cursor.execute(sql, [no])
            request.session['hit'] = 0
        
        # 이전 글 번호 가져오기
        sql = '''
                    SELECT NVL(MAX(NO),0)
                    FROM BOARD_TABLE1
                    WHERE NO < %s 

                '''
        cursor.execute(sql, [no])
        prev = cursor.fetchone()



        # 다음 글 번호 가져오기
        sql = '''
                    SELECT NVL(MIN(NO),0)
                    FROM BOARD_TABLE1
                    WHERE NO > %s 

                '''
        cursor.execute(sql, [no])
        next = cursor.fetchone()
        
        
        # 게시물 내용 가져오기 
        sql = '''
        SELECT 
        NO, TITLE, CONTENT, WRITER, HIT, TO_CHAR(REGDATE, 'YYYY-MM-DD HH:MI:SS'), IMG 
        FROM BOARD_TABLE1
        WHERE NO = %s
        '''
        cursor.execute(sql, [no])
        data = cursor.fetchone()
        print(data) # DB에서 받은 게시물 1개의 정보 출력 
        
        if data[6]: # DB에 BLOB로 있는 경우 
            img = data[6].read() # 바이트 배열을 img에 넣음
            img64 = b64encode(img).decode('utf-8')
        
        else: 
            file = open('./static/img/noImg.png', 'rb')
            img = file.read() # 바이트 배열을 img에 넣음
            img64 = b64encode(img).decode('utf-8')

        #print(no)
        return render(request,'board/content.html', {'one':data, 'image':img64, 'prev':prev[0], 'next':next[0]})


@csrf_exempt
def delete(request):
    if request.method == 'GET':
        
        # 127.0.0.1:8000/board/delete?no=37 >> "no"
        # 127.0.0.1:8000/board/delete >> 0
        no = request.GET.get("no",0)

        sql = '''
                DELETE FROM BOARD_TABLE1
                WHERE NO = %s
                '''

        cursor.execute(sql, [no])
        return redirect("/board/list")



@csrf_exempt
def edit(request):
    if request.method == 'GET':
        no = request.GET.get("no",0)
        sql = '''
                SELECT NO, TITLE, CONTENT
                FROM BOARD_TABLE1
                WHERE NO = %s
            '''
        cursor.execute(sql,[no])
        data = cursor.fetchone()
        return render(request, 'board/edit.html',{'one':data})

    
    elif request.method == 'POST':
        no = request.POST['no']
        ti = request.POST['title']
        co = request.POST['content']

        arr = [ti,co,no]

        sql = '''
                UPDATE BOARD_TABLE1 SET TITLE = %s, CONTENT = %s 
                WHERE NO = %s
            '''

        cursor.execute(sql, arr)
        return redirect("/board/content?no="+no)
@csrf_exempt
def select(request):


    
    #int()안써주고 그냥 받으면 문자로 나와서 int()로 감싸주기!
    txt = request.GET.get("text","")
    page = int(request.GET.get('page',1)) 
    
    
    # SELECT * FROM MEMBER_TABLE1
    #각 페이지 하나당 데이터 10개만 뜨게 만들기
    # 페이지 번호 1 >> 0,10
    # 페이지 번호 2 >> 10,20
    # 페이지 번호 3 >> 20,30 
   
    if txt=="": 
        #검색어가 없는 경우 
        # SELECT * FROM MEMBER_TABLE1
        #각 페이지 하나당 데이터 10개만 뜨게 만들기
        # 페이지 번호 1 >> 0,10
        # 페이지 번호 2 >> 10,20
        # 페이지 번호 3 >> 20,30 

        '''
        oracle 사용해서 sql문으로 5번째 ~ 9번째 데이터 가져오려면 
        SELECT * FROM(
                SELECT 
                    NO, TITLE, CONTENT, ROW_NUMBER() OVER (ORDER BY NO DESC) ROWN 
                    # 여기서 ROWN는 기존 테이블에 열 하나 더 추가해서 데이터 순서대로 번호 넣어줌...(?)

                FROM 
                     BOARD_TABLE1
                        )
        WHERE ROWN BETWEEN 5 AND 9; 

        '''

        '''
        ##한글이 포함된 항목 조회 
        SELECT * FROM BOARD_TABLE1
        WHERE NAME LIKE '%'||'한글'||'%';

        '''

        list = Table1.objects.all()[(page-1)*10 : page*10] 

        # SELECT COUNT(*) FROM MEMBER_TABLE2
        cnt = Table1.objects.all().count()
        tot = (cnt-1)//10 + 1
        # 예) 게시물 13개이면 >> 2페이지
        # 예) 게시물 10개이면 >> 1페이지
        # 예) 게시물 20개이면 >> 2페이지 
    
    else: # 검색어가 있는 경우
        # SELECT * FROM MEMBER_TABLE1 WHERE writer LIKE '%가%'
        list = Table1.objects.filter(writer__contains = txt)[(page-1)*10 : page*10]

        # SELECT COUNT(*) FROM MEMBER_TABLE1 WHERE writer LIKE '%가%'
        cnt = Table1.objects.filter(writer__contains = txt).count()

        tot = (cnt-1)//10+1
    
    return render(request, 'board/select.html', {'abc':list, 'pages':range(1,tot+1,1)})


##################################################################################
# TABLE2에 데이터 추가(입력)시키기
@csrf_exempt
def t2_insert(request):
    if request.method == 'GET':
        return render(request, 'board/t2_insert.html')
    
    elif request.method == 'POST':
        obj = Table2() #obj객체 생성
        obj.name = request.POST['name'] # 변수에 값 
        obj.kor = request.POST['kor']
        obj.eng = request.POST['eng']
        obj.math = request.POST['math']
        obj.save()

        
        
        return redirect('/board/t2_insert')

# TABLE2 리스트  
@csrf_exempt
def t2_list(request):
    if request.method == 'GET':
        rows = Table2.objects.all() # 이 문장을 sql로 표현하면 SELECT * FROM BOARD_TABLE2
        print(rows) # 결과 확인
        print(type(rows)) # 타입 확인 
        return render(request, 'board/t2_list.html', {'list':rows}) # html 표시, # html에서는 list로 써주기!


# TABLE2 데이터 삭제 하기 
@csrf_exempt
def t2_delete(request):
    if request.method == 'GET':
        n= request.GET.get('no',0)
        row = Table2.objects.get(no=n)
        # 이 문장을 sql로 표현하면 SELECT * FROM BOARD_TABLE2 WHERE NO = %s
        row.delete() # 삭제
        return redirect('/board/t2_list')

# TABLE2 수정하기 
@csrf_exempt
def t2_update(request):
    if request.method == 'GET':
        n= request.GET.get('no',0)
        row = Table2.objects.get(no=n)
        # 이 문장을 sql로 표현하면 SELECT * FROM BOARD_TABLE2 WHERE NO = %s
        row.delete() # 삭제
        return render(request, '/board/t2_update.html', {'one':row})


    elif request.method == 'POST':
        n= request.POST['no']

        obj = Table2.objects.get(no=n) #obj객체 생성
        obj.name = request.POST['name'] # 변수에 값 
        obj.kor = request.POST['kor']
        obj.eng = request.POST['eng']
        obj.math = request.POST['math']
        obj.save() 
        
        # obj.save()는 
        # UPDATE BOARD_TABLE2 
        # SET NAME = %s, KOR = %s, ENG = %s, MATH = %s
        # WHERE NO = %s 와 동일 

        
        
        return redirect('/board/t2_list')


# TABLE2에 일괄 추가 시키기 
def t2_insert_all(request):
    if request.method == 'GET':
        return render(request, 'board/t2_insert_all.html')
    
    elif request.method == 'POST':
        na = request.POST.getlist('name[]')
        ko = request.POST.getlist('kor[]')
        en = request.POST.getlist('eng[]')
        ma = request.POST.getlist('math[]')

        '''
        하나 할 때는 가능, but 동시에 수행할 땐 save 쓰면 안 됨
        b/c 반복문 수행하다가 중간에 끊기면 다 날아감......ㅠㅠ
        대신 Table2.objects.bulk_create(objs)처럼 일괄 추가해야 함!! ^_^
        '''
        
        objs = []
        
        for i in range(0,len(na),1):
            obj = Table2()
            obj.name = na[i]
            obj.kor = ko[i]
            obj.eng = en[i]
            obj.math = ma[i]
            objs.append(obj)

        Table2.objects.bulk_create(objs)
        return redirect('/board/t2_list')
        
# TABLE2 체크 된 거 일괄 수정 시키기 
def t2_update_all(request):
    if request.method == 'GET':
        n = request.session['no'] 
        #예를 들어 8,5,3번만 선택되었다면 n = [8,5,3]
        # rows = Table2.objects.raw("SELECT * FROM BOARD_TABLE2 WHERE NO IN (8,5,3)")
        #또는 SELECT * FROM BOARD_TABLE2 WHERE NO =8 OR NO =5 OR NO = 3으로 표현 
        rows = Table2.objects.filter(no__in = n)
        return render(request, 'board/t2_update_all.html', {'list': rows})
        
     
    elif request.method == 'POST':
        menu = request.POST['menu']
        
        # t2_list.html의 일괄 수정 버튼 눌렀을 때 
        if menu == '1':
            no = request.POST.getlist("chk[]")
            request.session['no']  = no #세션 사용하기 b/c 화면을 바꾸면 no가 소멸되기 때문에 세션을 이용하여 해결 
            print(no) # 체크된 번호 prompt창에 출력 
            return redirect("/board/t2_update_all")

        
        # t2_update_all.html의 일괄 수정 버튼 눌렀을 때
        elif menu == '2':
            no = request.POST.getlist('no[]')
            name = request.POST.getlist('name[]')
            kor = request.POST.getlist('kor[]')
            eng = request.POST.getlist('eng[]')
            math = request.POST.getlist('math[]')

            objs = []
            for i in range(0, len(no), 1):
                obj = Table2.objects.get(no= no[i])
                obj.name = name[i]
                obj.kor = kor[i]
                obj.eng = eng[i]
                obj.math = math[i]
                objs.append(obj)
            
            Table2.objects.bulk_update(objs,["name", "kor", "eng", "math"])
            return redirect("/board/t2_list")


        

        






