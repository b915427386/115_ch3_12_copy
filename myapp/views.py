from django.shortcuts import render
from django.http import HttpResponse            # 用於返回HTTP響應
from django.shortcuts import redirect           # 用於重定向到其他URL
from myapp.models import *                      # 導入所有模型類
from django.forms.models import model_to_dict   # 用於將模型實例轉換為字典

# Create your views here.
def search_list(request):
    if 'cname' in request.GET:
        cname = request.GET['cname']
        print("搜尋的姓名:", cname)
        # orm語法: 根據姓名查詢學生並按班級ID排序
        resultList = students.objects.filter(cname__icontains=cname).order_by('-cid')   
    else:
        # orm語法: 查詢所有學生並按班級ID排序
        resultList = students.objects.all().order_by('-cid')
        for student in resultList:
            print(model_to_dict(student))

    # resultList = []   # 測試用, 清空查詢結果
    errormessage = ""
    if not resultList:
        errormessage = "查無學生資料"

    # return render(request, 'search_list.html', {'resultList': resultList})
    # 使用locals()將所有本地變量傳遞給模板
    return render(request, 'search_list.html', locals())

def search_name(request):
    return render(request, 'search_name.html', locals())

def index(request):
    if 'site_search' in request.GET:
        site_search = request.GET['site_search']
        site_search = site_search.strip()  # 去除前後空白
        keywords = site_search.strip()  # 將搜尋關鍵字去除前後空白後存入 keyword 變量
        print(f"搜尋的輸入: {site_search} , 關鍵字: {keywords}")
        # 多個關鍵字搜尋, 搜尋 cname,cbirthday,cemail,cphone,caddr
        from django.db.models import Q
        query = Q()
        for keyword in keywords.split():
            query |= \
                Q(cname__icontains=keyword) | \
                Q(cbirthday__icontains=keyword) | \
                Q(cemail__icontains=keyword) | \
                Q(cphone__icontains=keyword) | \
                Q(caddr__icontains=keyword)
        resultList = students.objects.filter(query).order_by('cid')
        
    else:
        resultList = students.objects.all().order_by('cid')

    for data in resultList:
        print(model_to_dict(data))
    errorMessage = ""
    status = True
    #resultList = [] # 測試 if空結果的異常情況

    if not resultList:
        errorMessage = "查無學生資料"
        status = False
        data_count = 0     # 當查無學生資料時, 直接設置資料筆數為0
    else:
        data_count = resultList.count()     # 計算學生資料筆數

    print(f"錯誤訊息: {errorMessage}")
    print(f"資料筆數: {data_count}")

    # 分頁設置, 每頁顯示3筆
    from django.core.paginator import Paginator
    paginator = Paginator(resultList, 5)        # 每頁顯示5筆
    page_number = request.GET.get('page')       # 取得當前頁碼
    page_obj = paginator.get_page(page_number)  # 取得當前頁的分頁object
    # pagination 說明:
    # page_obj 是一個包含該頁資料的物件
    # page_obj.number 目前頁碼
    # page_obj.paginator.num_pages 總頁數
    # page_obj.paginator.page_range 所有可用的頁碼（從 1 開始）
    # page_obj.previous_page_number 上一頁的頁碼
    # page_obj.next_page_number 下一頁的頁碼
    # page_obj.has_next 是否有下一頁
    # page_obj.has_previous 是否有上一頁
    # page_obj.object_list 該頁的資料
    
    return render(request, 'index.html', locals())

def post(request):
    if request.method == 'POST':
        # 在這裡處理POST請求的邏輯
        # return HttpResponse("<h1 style='color:green;font-size:100px;text-align:center;'>POST request received</h1>")
        cname = request.POST.get('cname')
        csex = request.POST.get('csex')
        cbirthday = request.POST.get('cbirthday')
        cemail = request.POST.get('cemail')
        cphone = request.POST.get('cphone')
        caddr = request.POST.get('caddr')
        print(f"姓名: {cname}, 性別: {csex}, 生日: {cbirthday}, 信箱: {cemail}, 電話: {cphone}, 地址: {caddr}")

        # 創建新的學生資料, 並保存到資料庫
        new_student = students(
            cname=cname,
            csex=csex,
            cbirthday=cbirthday,
            cemail=cemail,
            cphone=cphone,
            caddr=caddr
        )
        new_student.save()

        return redirect('index')    # 新增完成後, 重新導向到首頁
    else:
        #return HttpResponse("<h1 style='color:blue;font-size:100px;text-align:center;'>Hello Everyone</h1>")
        return render(request, 'post.html', locals())

def edit(request, id):
    if request.method == 'POST':
        cname = request.POST.get('cname')
        csex = request.POST.get('csex')
        cbirthday = request.POST.get('cbirthday')
        cemail = request.POST.get('cemail')
        cphone = request.POST.get('cphone')
        caddr = request.POST.get('caddr')
        print(f"姓名: {cname}, 性別: {csex}, 生日: {cbirthday}, 信箱: {cemail}, 電話: {cphone}, 地址: {caddr}")

        # 修改後更新DB指定ID的學生資料
        edit_student = students.objects.filter(cid=id).update(
            cname=cname,
            csex=csex,
            cbirthday=cbirthday,
            cemail=cemail,
            cphone=cphone,
            caddr=caddr
        )

        #return HttpResponse("<h1 style='text-align:center;'>POST request received for student ID: {}</h1>".format(id))
        return redirect('index')    # 修改完成後, 重新導向到首頁
    else:
        print(f"ID: {id}")
        obj_data = students.objects.get(cid=id)
        print(model_to_dict(obj_data))

        #return HttpResponse("<h1 style='color:blue;font-size:100px;text-align:center;'>Edit request received for student ID: {}</h1>".format(id))
        return render(request, 'edit.html', locals())

def delete(request, id):
    if request.method == 'POST':
        # 刪除指定ID的學生資料
        print(f"正在刪除學生 ID: {id}")
        students.objects.filter(cid=id).delete()

        #return HttpResponse("<h1 style='text-align:center;'>POST request received for <strong style='color:red;'>DELETE student ID: {}</strong></h1>".format(id))
        return redirect('index')    # 刪除完成後, 重新導向到首頁
    else:
        print(f"ID: {id}")
        # 獲取要刪除的ID對應的學生資料
        obj_data = students.objects.get(cid=id)
        print(model_to_dict(obj_data))
        #return HttpResponse("<h1 style='text-align:center;'>GET request received for <strong style='color:red;'>DELETE student ID: {}</strong></h1>".format(id))
        return render(request, 'delete.html', locals())

from django.http import JsonResponse
def getAllItems(request):
    result = students.objects.all().order_by('cid')
    # for item in result:
    #     print(model_to_dict(item))
    resultList = list(result.values())  # 將QuerySet轉換為列表，其中每個元素都是字典，以便JsonResponse可以正確處理
    print(resultList)   # 輸出結果列表以便在控制台查看, 如果是QuerySet(物件)則不能直接查看其內容, 轉換為列表後可以直接查看
    return JsonResponse(resultList, safe=False)     # 返回所有學生資料的JSON響應, 其中 safe=False : 允許返回非字典對象

def getItem(request, id):
    try:
        item = students.objects.get(cid=id)
        result = model_to_dict(item)
        print(result)   # 輸出結果以便在控制台查看
        return JsonResponse(result, safe=False)     # 返回指定ID的學生資料的JSON響應
    except students.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

from django.views.decorators.csrf import csrf_exempt    # 用於取消CSRF驗證, 方便API測試
@csrf_exempt    # 針對 createItem view, 取消CSRF驗證, 允許API測試時不需要CSRF Token
def createItem(request):
    try:
        if request.method == 'GET':
            cname = request.GET.get('cname')
            csex = request.GET.get('csex')
            cbirthday = request.GET.get('cbirthday')
            cemail = request.GET.get('cemail')
            cphone = request.GET.get('cphone')
            caddr = request.GET.get('caddr')
            print("=========== GET ==========")
            print(f"姓名: {cname}, 性別: {csex}, 生日: {cbirthday}, 信箱: {cemail}, 電話: {cphone}, 地址: {caddr}")
        elif request.method == 'POST':
            cname = request.POST['cname']
            csex = request.POST['csex']
            cbirthday = request.POST['cbirthday']
            cemail = request.POST['cemail']
            cphone = request.POST['cphone']
            caddr = request.POST['caddr']
            print("=========== POST ==========")
            print(f"姓名: {cname}, 性別: {csex}, 生日: {cbirthday}, 信箱: {cemail}, 電話: {cphone}, 地址: {caddr}")
    except:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        # orm 建立新學生資料
        new_student = students.objects.create(
            cname=cname,
            csex=csex,
            cbirthday=cbirthday,
            cemail=cemail,
            cphone=cphone,
            caddr=caddr
        )
        return JsonResponse({"message": "Student created successfully"}, safe=True)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    #return HttpResponse("<h1 style='text-align:center;'>This is the student create view</h1>")

@csrf_exempt    # 針對 updateItem view, 取消CSRF驗證, 允許API測試時不需要CSRF Token
def updateItem(request, id):
    try:
        item = students.objects.get(cid=id)
        if request.method == 'GET':
            item.cname = request.GET.get('cname', item.cname)
            item.csex = request.GET.get('csex', item.csex)
            item.cbirthday = request.GET.get('cbirthday', item.cbirthday)
            item.cemail = request.GET.get('cemail', item.cemail)
            item.cphone = request.GET.get('cphone', item.cphone)
            item.caddr = request.GET.get('caddr', item.caddr)
        elif request.method == 'POST':
            item.cname = request.POST['cname']
            item.csex = request.POST['csex']
            item.cbirthday = request.POST['cbirthday']
            item.cemail = request.POST['cemail']
            item.cphone = request.POST['cphone']
            item.caddr = request.POST['caddr']
        item.save()
        return JsonResponse({"message": "Student updated successfully"}, safe=True)
    except students.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt    # 針對 deleteItem view, 取消CSRF驗證, 允許API測試時不需要CSRF Token
def deleteItem(request, id):
    try:
        item = students.objects.get(cid=id)
        item.delete()
        return JsonResponse({"message": "Student deleted successfully"}, safe=True)
    except students.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)