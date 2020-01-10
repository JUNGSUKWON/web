
from django.shortcuts import render, redirect
from django.http import HttpResponse

# join에서 post 했을 때, 크롬에서 보안 문제 걸리는 것을 해결하기 위해 csrf_exempt 사용
from django.views.decorators.csrf import csrf_exempt
from django.db import connection # 쿼리를 쓰기 위해서는 connection이 필요함
# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth import authenticate as auth1 # 나중에 헷갈릴까봐 별칭 사용 
from django.contrib.auth import login as login1 # 우리가 만들었던 함수랑 이름 겹쳐서 별칭 사용해줘야함 
from django.contrib.auth import logout as logout1 # 우리가 만들었던 함수랑 이름 겹쳐서 별칭 사용해줘야함 
cursor = connection.cursor() # cursor를 통해서만 execute가능함
from .models import Table2 # models.py 파일의 Table2클래스, 모델 사용 위해 가져옴 


@csrf_exempt
def js_index(request):
    return render(request, 'member/js_index.html')

@csrf_exempt
def js_chart(request):
    str = '100,200,300,400,200,100'
    return render(request, 'member/js_chart.html', {"str":str})

#################################################################

def auth_join(request):
    if request.method == 'GET':
        return render(request, 'member/auth_join.html')
    
    elif request.method == 'POST':
        id = request.POST['username']
        pw = request.POST['password']
        na = request.POST['first_name']
        em = request.POST['email']

        # 회원가입
        # User.~~ 이거 쓰려면 위에 from django.contrib.auth.models import User 써야 함! 
        # 암호화 시키려면 이 방식으로 써야 함!! 
        obj = User.objects.create_user(  
            username = id,
            password = pw,
            first_name = na,
            email = em
        )
        obj.save()
        return redirect('/member/auth_index')

@csrf_exempt
def auth_index(request):
    if request.method == 'GET':
        return render(request,'member/auth_index.html')


def auth_login(request):
    if request.method == 'GET':
        return render(request, 'member/auth_login.html')
    elif request.method == 'POST':
        id = request.POST['username']
        pw = request.POST['password']
        
        # DB에 인증
        obj = auth1(request, username = id, password = pw)

        if obj is not None:
            login1(request,obj) # 세션에 추가
            return redirect('/member/auth_index')
        
        return redirect('/member/auth_index')

def auth_logout(request):
    if request.method == 'GET' or request.method == 'POST':
        logout1(request) #세션 초기화 
        return redirect('/member/auth_index')

def auth_edit(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect("/member/auth_login")
        obj = User.objects.get(username = request.user)
        return render(request, 'member/auth_edit.html', {'obj':obj})

    elif request.method == 'POST':
        id = request.POST['username']
        na = request.POST['first_name']
        em = request.POST['email']

        obj = User.objects.get(username=id)
        obj.first_name = na
        obj.email = em
        obj.save()
        return redirect('/member.index')

def auth_pw(request):
    if request.method == 'GET':
        if not request.user.is_authenticated :
            return redirect('/member/auth_login')
        
        return render(request,'member/auth_pw.html')
    
    elif request.method == 'POST':
        pw = request.POST['pw']
        pw1 = request.POST['pw1']

        #바꾸기 전에 인증
        obj = auth1(request, username = request.user, password = pw)

        if obj:
            obj.set_password(pw1)
            obj.save()
            return redirect('/member/auth_index')
        
        return redirect('/member/auth_pw')

            
        
        
    


@csrf_exempt
def index(request):
    #return HttpResponse('index page <hr/>')
    return render(request, 'member/index.html')

@csrf_exempt
def login(request):
    if request.method == 'GET':
        return render(request, 'member/login.html')
    
    elif request.method == 'POST':
        ar = [request.POST['id'], request.POST['pw']]
        sql = '''
        SELECT ID, NAME FROM MEMBER WHERE ID = %s AND PW = %s
        '''
        cursor.execute(sql, ar)
        data = cursor.fetchone() # 한 줄 가져오기
        print(type(data))
        print(data)
    if data: 
        request.session['userid'] = data[0]
        request.session['username'] = data[1] 
        return redirect('/member/index')
    
    return redirect('/member/login')

@csrf_exempt
def logout(request):
    if request.method == 'GET' or request.method =='POST':
        del request.session['userid']
        del request.session['username']
        return redirect('/member/index')


@csrf_exempt #post로 값을 전달 받는 곳은 필수 
def join(request):
    if request.method == 'GET':
        return render(request, 'member/join.html') 
    
    elif request.method == 'POST':
        #앞에 /넣으면 절대 기호로 사용됨(ip 주소 뒤에 /~~ 바로 붙음) 
        # html에서 넘어오는 값 받기
        na = request.POST['name']
        ag= request.POST['age']
        pw = request.POST['pw']

        ar = [request.POST['id'], na, ag, pw]
        print(ar)
        # DB에 추가함

        
        sql = '''
                INSERT INTO member(ID,NAME,AGE,PW,JOINDATE)
                VALUES (%s, %s, %s, %s, SYSDATE)
        
            '''
        cursor.execute(sql, ar)

        # 크롬에서 127.00.1:8000/member/index 엔터키를 자동화
        return redirect('/member/index') 


def list(request):
    # ID기준으로 오름차순 
    sql = "SELECT * FROM MEMBER ORDER BY ID ASC"
    cursor.execute(sql) #sql문 실행
    data = cursor.fetchall() # 결과값을 가져옴
    print(type(data)) 
    print(data)

    # list 변수에 data값을, title 변수에 "회원목록" 문자를 
    return render(request, 'member/list.html', {"list":data, "title":"회원목록"})


@csrf_exempt #post로 값을 전달 받는 곳은 필수 
def edit(request):
    if request.method == 'GET':
        ar = [request.session['userid']]
        sql = '''
                SELECT * FROM MEMBER WHERE ID = %s
            '''

        cursor.execute(sql,ar)
        data = cursor.fetchone()
        print(data)
        
        return render(request, 'member/edit.html', {'one':data}) 

    elif request.method == 'POST':
        
        ar = [
            
            request.POST['name'],
            request.POST['age'],
            request.POST['id'],
            ]

        sql = '''
                UPDATE MEMBER SET NAME = %s, AGE = %s
                WHERE ID = %s
            '''
       
        cursor.execute(sql, ar) 
        
        request.session['username'] = request.POST['name'] 
        return redirect('/member/index') 


@csrf_exempt #post로 값을 전달 받는 곳은 필수 
def join1(request):
    if request.method == 'GET':
        return render(request, 'member/join1.html')

@csrf_exempt
def delete(request):
    if request.method == 'GET' or request.method == 'POST':
        ar = [request.session['userid']]
        sql = 'DELETE FROM MEMBER WHERE ID = %s'
        cursor.execute(sql, ar)

        return redirect("/member/logout")

##########################################################################
# exam_ 으로 시작하는 건 실습과제용 함수 
def exam_list(request):
    if request.method == 'GET':
        rows = Table2.objects.all()
        return render(request, 'member/exam_list.html', {'list':rows})

    if request.method == 'POST':
         return redirect('/member/exam_update_all')


def exam_insert(request): 
    if request.method == 'GET':
        return render(request, 'member/exam_insert.html')

    elif request.method == 'POST':
        na = request.POST.getlist('name[]')
        ko = request.POST.getlist('kor[]')
        en = request.POST.getlist('eng[]')
        ma = request.POST.getlist('math[]')
        crm = request.POST.getlist('classroom[]')

        objs = []
        for i in range(0, len(na),1):
            obj = Table2()
            obj.name = na[i]
            obj.kor = ko[i]
            obj.eng = en[i]
            obj.math = ma[i]
            obj.classroom = crm[i]
            objs.append(obj)
        
        Table2.objects.bulk_create(objs)
        return redirect('/member/exam_insert')


@csrf_exempt
def exam_update(request):
    if request.method == 'GET':
        n= request.GET.get('no',0)
        row = Table2.objects.get(no=n)
        row.delete()
        return render(request, 'member/exam_update.html', {'one':row})

    elif request.method == 'POST':
        n= request.POST['no']

        obj = Table2.objects.get(no=n) #obj객체 생성
        obj.name = request.POST['name'] # 변수에 값 
        obj.kor = request.POST['kor']
        obj.eng = request.POST['eng']
        obj.math = request.POST['math']
        obj.classroom = request.POST['classroom']
        obj.save()

        return redirect('/member/exam_list')


def exam_update_all(request):
    if request.method == 'GET':
        n = request.session['no'] 
        print(n)
        #예를 들어 8,5,3번만 선택되었다면 n = [8,5,3]
        # rows = Table2.objects.raw("SELECT * FROM BOARD_TABLE2 WHERE NO IN (8,5,3)")
        #또는 SELECT * FROM BOARD_TABLE2 WHERE NO =8 OR NO =5 OR NO = 3으로 표현 
        rows = Table2.objects.filter(no__in = n)
        return render(request, 'member/exam_update_all.html', {'list': rows})
        
     
    elif request.method == 'POST':
        menu = request.POST['menu']
        
        # exam_list.html의 일괄 수정 버튼 눌렀을 때 
        if menu == '1':
            no = request.POST.getlist("chk[]")
            print(no)
            request.session['no']  = no #세션 사용하기 b/c 화면을 바꾸면 no가 소멸되기 때문에 세션을 이용하여 해결 
             
            return redirect("/member/exam_update_all") # redirect는 주소

        
        # exam_update_all.html의 일괄 수정 버튼 눌렀을 때
        elif menu == '2':
            no = request.POST.getlist('no[]')
            name = request.POST.getlist('name[]')
            kor = request.POST.getlist('kor[]')
            eng = request.POST.getlist('eng[]')
            math = request.POST.getlist('math[]')
            classroom = request.POST.getlist('classroom[]')

            objs = []
            for i in range(0, len(no), 1):
                obj = Table2.objects.get(no= no[i])
                obj.name = name[i]
                obj.kor = kor[i]
                obj.eng = eng[i]
                obj.math = math[i]
                obj.classroom = classroom[i]
                objs.append(obj)
            
            Table2.objects.bulk_update(objs,["name", "kor", "eng", "math", "classroom"])
            return redirect("/member/exam_list")


@csrf_exempt
def exam_delete(request):
    if request.method == 'GET':
        n= request.GET.get('no',0)
        row = Table2.objects.get(no=n)
        # 이 문장을 sql로 표현하면 SELECT * FROM BOARD_TABLE2 WHERE NO = %s
        row.delete() # 삭제
        return redirect('/member/exam_list')


@csrf_exempt
def exam_select(request):
    
    #int()안써주고 그냥 받으면 문자로 나와서 int()로 감싸주기!
    txt = request.GET.get("text","")
    page = int(request.GET.get('page',1)) 
    
    
    # SELECT * FROM MEMBER_TABLE2
    #각 페이지 하나당 데이터 10개만 뜨게 만들기
    # 페이지 번호 1 >> 0,10
    # 페이지 번호 2 >> 10,20
    # 페이지 번호 3 >> 20,30 
   
    if txt=="": 
        #검색어가 없는 경우 
        # SELECT * FROM MEMBER_TABLE2
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

        list = Table2.objects.all()[(page-1)*10 : page*10] 

        # SELECT COUNT(*) FROM MEMBER_TABLE2
        cnt = Table2.objects.all().count()
        tot = (cnt-1)//10 + 1
        # 예) 게시물 13개이면 >> 2페이지
        # 예) 게시물 10개이면 >> 1페이지
        # 예) 게시물 20개이면 >> 2페이지 
    
    else: # 검색어가 있는 경우
        # SELECT * FROM MEMBER_TABLE2 WHERE name LIKE '%가%'
        list = Table2.objects.filter(name__contains = txt)[(page-1)*10 : page*10]

        # SELECT COUNT(*) FROM MEMBER_TABLE2 WHERE name LIKE '%가%'
        cnt = Table2.objects.filter(name__contains = txt).count()

        tot = (cnt-1)//10+1
    
    return render(request, 'member/exam_select.html', {'list':list, 'pages':range(1,tot+1,1)})



    
    
