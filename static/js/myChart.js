<script type="text/javascript">
    alert"in js "
            $(function() {
    $( "#button2" ).click(function() {
        //Reboot Count js
        alert("button2")
        new Chart(document.getElementById("reboot-bar-chart"), {
        type: 'bar',
        data: {
          datasets: [
            {
              label: "Reboot Count",
              backgroundColor: {{ bg_color_reboot_selected|safe }},
              data: {{ device_reboot_selected }}
            }
          ],
          labels: {{ device_ips_selected|safe }}
        },
        options: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Device Reboot Count'
          }
        }
        });
        //Crash Count js
        new Chart(document.getElementById("crash-bar-chart"), {
        type: 'bar',
        data: {
          datasets: [
            {
              label: "Crash Count",
              backgroundColor: {{ bg_color_cpu_selected|safe }},
              data: {{ device_crash_selected }}
            }
          ],
          labels: {{ device_ips_selected|safe }}
        },
        options: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Device Crash Count'
          }
        }
        });
        //Memory Statistics

        var memoryData = {
          labels: {{ date_list|safe }},
          datasets: {{ memory_values_selected|safe }}
        };
        var memoryChartOptions = {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: 80,
                    fontColor: 'black'
                }
            },
            title: {
              display: true,
                text: 'Device Memory in mb'
          }
        };
        new Chart(document.getElementById("memory-line-chart"), {
          type: 'line',
          data: memoryData,
          options: memoryChartOptions
        });
        //CPU charts
          var cpuData = {
          labels: {{ date_list|safe }},
          datasets: {{ cpu_values_selected|safe }}
        };
        var cpuChartOptions = {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: 80,
                    fontColor: 'black'
                }
            },
            title: {
              display: true,
                text: 'CPU usage'
          }

        };
        new Chart(document.getElementById("cpu-line-chart"), {
          type: 'line',
          data: cpuData,
          options: cpuChartOptions
        });
    });
});
</script>
<script type="text/javascript">
$(function() {
     $("#button1").click(function() {
        //Reboot Count js
        alert("button1")
        new Chart(document.getElementById("reboot-bar-chart"), {
        type: 'bar',
        data: {
          datasets: [
            {
              label: "Reboot Count",
              backgroundColor: {{ bg_color_reboot_week|safe }},
              data: {{ device_reboot_week }}
            }
          ],
          labels: {{ device_ips_week|safe }}
        },
        options: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Device Reboot Count'
          }
        }
        });
        //Crash Count js
        new Chart(document.getElementById("crash-bar-chart"), {
        type: 'bar',
        data: {
          datasets: [
            {
              label: "Crash Count",
              backgroundColor: {{ bg_color_cpu_week|safe }},
              data: {{ device_crash_week }}
            }
          ],
          labels: {{ device_ips_week|safe }}
        },
        options: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Device Crash Count'
          }
        }
        });
        //Memory Statistics

        var memoryData = {
          labels: {{ week_date_list|safe }},
          datasets: {{ memory_values_week|safe }}
        };
        var memoryChartOptions = {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: 80,
                    fontColor: 'black'
                }
            },
            title: {
              display: true,
                text: 'Device Memory in mb'
          }
        };
        new Chart(document.getElementById("memory-line-chart"), {
          type: 'line',
          data: memoryData,
          options: memoryChartOptions
        });
        //CPU charts
          var cpuData = {
          labels: {{ week_date_list|safe }},
          datasets: {{ cpu_values_week|safe }}
        };
        var cpuChartOptions = {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: 80,
                    fontColor: 'black'
                }
            },
            title: {
              display: true,
                text: 'CPU usage'
          }

        };
        new Chart(document.getElementById("cpu-line-chart"), {
          type: 'line',
          data: cpuData,
          options: cpuChartOptions
        });
    });
});
</script>
