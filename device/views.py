from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from forms import DeviceDetails
from django.core.urlresolvers import reverse
from models import Device,Device_log
from django.db.models import Q
from django.http import HttpResponse,JsonResponse
import random
from datetime import datetime,timedelta,date
# Create your views here.

def index(request):
    my_dict = {'insert_me':"Hello from first app's view.py"}
    return render(request,'index.html',context=my_dict)

def device_details(request):
    if request.method == 'POST':
        # All details are provided
        ipadd_str = request.POST.get('ipadd')
        ipadd_list = ipadd_str.split(",")
        model = request.POST.get('model')
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        # print ipadd_list
        # print model
        global fromdate, todate
        fromdate = "-".join(fromdate.split("/")) + " 00:00:00"
        todate = "-".join(todate.split("/"))+ " 23:59:59"
        device_details_list = []
        # device_details_list = Device.objects.all()
        device_details_list.extend(Device.objects.filter(IP__in=ipadd_list, CREATED__lte=todate, CREATED__gte=fromdate))
        # print device_details_list
        device_details_dict = {'device':device_details_list}
        # device_details = {'device':[{'ipadd': ipadd, 'model': model, 'fromdate': fromdate, 'todate': todate}]}
        # Django's built-in authentication function:
        return render(request, 'device_details.html', context=device_details_dict)
    else:
        # Details are not provided
        return HttpResponseRedirect(reverse('index'))

def return_random_color(return_list = True,key_list=[]):
    if return_list:
        color_list = []
        for i in range(0, len(key_list)):
            r = lambda: random.randint(0, 255)
            color_list.append('#%02X%02X%02X' % (r(), r(), r()))
        return color_list
    else:
        r = lambda: random.randint(0, 255)
        return ('#%02X%02X%02X' % (r(), r(), r()))

def return_final_list(item_list):
    final_list = []
    for elem in item_list:
        if elem not in final_list:
            final_list.append(elem)
    for elem in final_list:
        elem.update({
        'lineTension': 0,
        'fill': 'false',
        'borderColor': return_random_color(return_list=False),
        'backgroundColor': 'transparent',
        'borderDash': [5, 5],
        'pointBorderColor': return_random_color(return_list=False),
        'pointBackgroundColor': 'rgba(255,150,0,0.5)',
        'pointRadius': 5,
        'pointHoverRadius': 10,
        'pointHitRadius': 30,
        'pointBorderWidth': 2,
        'pointStyle': 'rectRounded'})
    return final_list

def return_ip_reboot_cpu_dict(query_list,ip_list):
    reboot_dict,crash_dict = {},{}
    ip_list = []
    for query in query_list:
        print query.IP
        if query.IP not in ip_list:
            ip_list.append(query.IP)
        if query.IP in reboot_dict.keys():
            if str(query.REBOOTED) == str(True):
                reboot_dict[query.IP] += 1
            else:
                reboot_dict[query.IP] = 1
        else:
            reboot_dict[query.IP] = 0
        if query.IP in crash_dict.keys():
            if str(query.CRASHED) == str(True):
                crash_dict[query.IP] += 1
            else:
                crash_dict[query.IP] = 1
        else:
            crash_dict[query.IP] = 0
    print (ip_list, reboot_dict, crash_dict)
    return (ip_list, reboot_dict, crash_dict)

def return_memory_cpu_list(query_list, ip_list):
    memory_list, cpu_list = [], []
    for ip in ip_list:
        ip_query_list = query_list.filter(IP=ip)
        memory_data_list, cpu_data_list = [], []
        for query in ip_query_list:
            memory_data_list.append(int(query.MEMORY))
            cpu_data_list.append(int(query.CPU))
            memory_list.append({'label': str(ip),
                                'data': memory_data_list,
                                })
            cpu_list.append({'label': str(ip),
                             'data': cpu_data_list,
                             })
    return (memory_list,cpu_list)
def device_charts(request):
    if request.method == 'POST':
        # Django's built-in authentication function:
        device_charts_list, bg_color_list, memory_list, cpu_list, ip_list, date_list, final_memory_list_selected, final_cpu_list_selected = [], [], [], [], [], [], [], []
        reboot_dict, crash_dict, memory_dict = {}, {}, {}
        week_date_list = [str(datetime.now() - timedelta(days=i)).split(" ")[0] for i in range(0, 7)]
        last_24hr_time_list = [((datetime.now() - timedelta(hours=i)).strftime('%H:%M:%S')).split(":")[0] for i in
                               range(0, 24)]
        global fromdate, todate
        d1 = str(fromdate).split(" ")[0].split("-")
        d2 = str(todate).split(" ")[0].split("-")
        start_date = date(int(d1[0]), int(d1[1]), int(d1[2]))
        end_date = date(int(d2[0]), int(d2[1]), int(d2[2]))
        date_list = [str(start_date + timedelta(n)) for n in range(int((end_date - start_date).days))]
        # for selected dates
        device_charts_list = Device.objects.filter(CREATED__lte=todate, CREATED__gte=fromdate)
        (ip_list, reboot_dict_selected, crash_dict_selected) = return_ip_reboot_cpu_dict(device_charts_list,ip_list)
        key_list_selected = [str(key) for key in reboot_dict_selected.keys()]
        (memory_list,cpu_list) = return_memory_cpu_list(device_charts_list,ip_list)
        final_memory_list_selected = return_final_list(memory_list)
        final_cpu_list_selected = return_final_list(cpu_list)
        #for a week
        ip_list = []
        device_charts_list = Device.objects.filter(CREATED__gte=week_date_list[-1]+" 00:00:00",CREATED__lte=week_date_list[0]+" 23:59:59")
        (ip_list, reboot_dict_week, crash_dict_week) = return_ip_reboot_cpu_dict(device_charts_list,ip_list)
        key_list_week = [str(key) for key in reboot_dict_week.keys()]
        (memory_list,cpu_list) = return_memory_cpu_list(device_charts_list,ip_list)
        final_memory_list_selected_week = return_final_list(memory_list)
        final_cpu_list_selected_week = return_final_list(cpu_list)
        #for a day
        device_charts_list = Device.objects.filter(CREATED__lte=week_date_list[-1]+" 00:00:00")
        (ip_list, reboot_dict_day, crash_dict_day) = return_ip_reboot_cpu_dict(device_charts_list, ip_list)
        key_list_day = [str(key) for key in reboot_dict_day.keys()]
        (memory_list, cpu_list) = return_memory_cpu_list(device_charts_list, ip_list)
        final_memory_list_selected_day = return_final_list(memory_list)
        final_cpu_list_selected_day = return_final_list(cpu_list)

        device_charts_dict = {'device_ips_selected': key_list_selected ,
                              'device_ips_week': key_list_week,
                              'device_ips_day': key_list_day,
                              'device_reboot_selected':list(reboot_dict_selected.values()),
                              'device_crash_selected':list(crash_dict_selected.values()),
                              'device_reboot_week': list(reboot_dict_week.values()),
                              'device_crash_week': list(crash_dict_week.values()),
                              'device_reboot_day': list(reboot_dict_day.values()),
                              'device_crash_day': list(crash_dict_day.values()),
                              'one_day_list' : last_24hr_time_list,
                              'week_date_list':week_date_list,
                              'date_list': date_list,
                              'memory_values_selected': final_memory_list_selected,
                              'cpu_values_selected': final_cpu_list_selected,
                              'memory_values_week': final_memory_list_selected_week,
                              'cpu_values_week':final_cpu_list_selected_week,
                              'memory_values_day': final_memory_list_selected_day,
                              'cpu_values_day': final_cpu_list_selected_day,
                              'bg_color_reboot_selected': return_random_color(key_list=key_list_selected),
                              'bg_color_cpu_selected': return_random_color(key_list=key_list_selected),
                              'bg_color_reboot_week': return_random_color(key_list=key_list_week),
                              'bg_color_cpu_week': return_random_color(key_list=key_list_week),
                              'bg_color_reboot_day': return_random_color(key_list=key_list_day),
                              'bg_color_cpu_day': return_random_color(key_list=key_list_day)
                              }
        print device_charts_dict
        return JsonResponse(device_charts_dict)
        # return render(request, 'device_charts.html', context=device_charts_dict)
    else:
        return HttpResponseRedirect(reverse('index'))