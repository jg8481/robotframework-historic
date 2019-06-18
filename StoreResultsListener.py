import datetime
import sqlite3
from sqlite3 import Error
from robot.libraries.BuiltIn import BuiltIn

class StoreResultsListener:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
        self.PRE_RUNNER = 0
        self.start_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        self.date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Connect to db, if db doesn't exist create new one
        self.con = connect_to_sql_db()
        create_sql_tables(self.con)

    def start_suite(self, name, attrs):        
        self.test_count = len(attrs['tests'])
        self.suite_name =  name

    def start_test(self, name, attrs):
        self.t_start_time = datetime.datetime.now().time().strftime('%H:%M:%S')

    def end_test(self, name, attrs):
        if self.test_count != 0:
            self.total_tests += 1
        
        if attrs['status'] == 'PASS':
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.t_end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        self.t_total_time=(datetime.datetime.strptime(self.t_end_time,'%H:%M:%S') - datetime.datetime.strptime(self.t_start_time,'%H:%M:%S'))

        tentities = (str(self.date_now), str(self.suite_name) + " - " + str(name), str(attrs['status']), str(self.t_total_time), str(attrs['message']))
        insert_into_test_sql_table(self.con, tentities)

    def close(self):
        self.end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        self.total_time=(datetime.datetime.strptime(self.end_time,'%H:%M:%S') - datetime.datetime.strptime(self.start_time,'%H:%M:%S'))

        entities = (str(self.date_now), str(self.total_tests), str(self.passed_tests), str(self.failed_tests), str(self.total_time))
        insert_into_suite_sql_table(self.con, entities)
        generate_html_report(self.con)

'''

# * # * # * # * Re-usable methods out of class * # * # * # * #

''' 

def get_current_date_time(format,trim):
    t = datetime.datetime.now()
    if t.microsecond % 1000 >= 500:  # check if there will be rounding up
        t = t + datetime.timedelta(milliseconds=1)  # manually round up
    if trim:
        return t.strftime(format)[:-3]
    else:
        return t.strftime(format)

def connect_to_sql_db():
    try: 
        con = sqlite3.connect('historical_results_do_not_delete.db')
        return con 
    except Error: 
        print(Error)

def create_sql_tables(con): 
    cursorObj = con.cursor()
    try:
        cursorObj.execute("CREATE TABLE IF NOT EXISTS results(execution_date text, total_tests text, passed_tests text, failed_tests text, duration text)") 
        cursorObj.execute("CREATE TABLE IF NOT EXISTS tresults(execution_date text, test_case text, status text, duration text, msg text)") 
        con.commit()
    except Error:
        print(Error)

def insert_into_suite_sql_table(con, entities):
    cursorObj = con.cursor()
    cursorObj.execute('INSERT INTO results(execution_date, total_tests, passed_tests, failed_tests, duration) VALUES(?, ?, ?, ?, ?)', entities)
    con.commit()

def insert_into_test_sql_table(con, tentities):
    cursorObj = con.cursor()
    cursorObj.execute('INSERT INTO tresults(execution_date, test_case, status, duration, msg) VALUES(?, ?, ?, ?, ?)', tentities)
    con.commit()

def generate_html_report(con): 

    head = get_html_head_text()
    body = get_html_body()    
    script = get_html_footer()
    table_content = ""
    t_table_content = ""

    cursorObj = con.cursor() 
    cursorObj.execute('SELECT * FROM results') 
    rows = cursorObj.fetchall() 
    for row in rows:
        table_content += get_and_create_suite_table_content(row)
    
    cursorObj.execute('SELECT * FROM tresults') 
    rows = cursorObj.fetchall() 
    for row in rows:
        t_table_content += get_and_create_test_table_content(row)

    now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    record_name = 'HistoricResults-' + str(now) + ".html"
    historical_results_file = open(record_name,'w')

    body = body.replace("<suite_replace></suite_replace>",table_content)
    body = body.replace("<test_replace></test_replace>",t_table_content)
    
    page_content = str(head) + str(body) + str(script)
    historical_results_file.write(page_content)
    historical_results_file.close()

def get_html_head_text():
    head = """
    <!DOCTYPE doctype html>
    <html lang="en">

    <head>
        <link href="https://png.icons8.com/windows/50/000000/bot.png" rel="shortcut icon" type="image/x-icon" />
        <title>RF Historic Results</title>
        <meta charset="utf-8" />
        <meta content="width=device-width, initial-scale=1" name="viewport" />
        <link href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css" rel="stylesheet" />
        <link href="https://cdn.datatables.net/buttons/1.5.2/css/buttons.dataTables.min.css" rel="stylesheet" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" />
        <script src="https://code.jquery.com/jquery-3.3.1.js" type="text/javascript"></script>
        <!-- Bootstrap core Googleccharts -->
        <script src="https://www.gstatic.com/charts/loader.js" type="text/javascript"></script>
        <script type="text/javascript">
            google.charts.load('current', {
                packages: ['corechart']
            });
        </script>
        <!-- Bootstrap core Datatable-->
        <script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/dataTables.buttons.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.flash.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/pdfmake.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/vfs_fonts.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.html5.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.print.min.js" type="text/javascript"></script>
        <style>
            body {
                font-family: -apple-system, sans-serif;
            }
            
            .sidenav {
                height: 100%;
                width: 220px;
                position: fixed;
                z-index: 1;
                top: 0;
                left: 0;
                background-color: white;
                overflow-x: hidden;
                border-style: ridge;
            }
            
            .sidenav a {
                padding: 12px 10px 8px 12px;
                text-decoration: none;
                font-size: 18px;
                color: Black;
                display: block;
            }
            
            .main {
                padding-top: 10px;
            }
            
            @media screen and (max-height: 450px) {
                .sidenav {
                    padding-top: 15px;
                }
                .sidenav a {
                    font-size: 18px;
                }
            }
            
            .dt-buttons {
                margin-left: 5px;
            }
            
            .loader {
                position: fixed;
                left: 0px;
                top: 0px;
                width: 100%;
                height: 100%;
                z-index: 9999;
                background: url('https://www.downgraf.com/wp-content/uploads/2014/09/02-loading-blossom-2x.gif') 50% 50% no-repeat rgb(249, 249, 249);
            }
        </style>
    </head>
    """
    return head

def get_html_body():
    body = """
    <body>
    <div class="loader"></div>
    <div class="sidenav">
        <a><img src="https://cdn.pixabay.com/photo/2016/08/02/10/42/wifi-1563009_960_720.jpg" style="height:20vh;max-width:98%;" /></a>
        <a class="tablink" href="#" id="defaultOpen" onclick="openPage('dashboard', this, 'orange')">
            <i class="fa fa-dashboard"></i> Dashboard</a>
        <a class="tablink" href="#" onclick="openPage('metrics', this, 'orange');">
            <i class="fa fa-th-large"></i> Metrics</a>
        <a class="tablink" href="#" onclick="openPage('test_metrics', this, 'orange');">
			<i class="fa fa-th-large"></i> Test Metrics</a>
    </div>

    <div class="main col-md-9 ml-sm-auto col-lg-10 px-4">
        <div class="tabcontent" id="dashboard">
            <div class="d-flex flex-column flex-md-row align-items-center p-1 mb-3 bg-light border-bottom shadow-sm">
                <h5 class="my-0 mr-md-auto font-weight-normal"><i class="fa fa-dashboard"></i> Dashboard</h5>
            </div>
            <div class="col-md-12" style="background-color:white;height:350px;width:auto;border:groove;">
                <span style="font-weight:bold">Latest 10 Results Trend</span>
                <div id="testsBarID" style="height:300px;width:auto;"></div>
            </div>
            <script>
                window.onload = function(){
                					executeDataTable('#sm',0);
                					createBarGraph('#sm', 0, 2, 3, 10, 'testsBarID', 'Executed On', 'Pass', 'Fail')
                					executeDataTable('#tm',0);
                				};
            </script>

            <div class="row">
                <div class="col-md-12" style="height:25px;width:auto;">
                    <p class="text-muted" style="text-align:center;font-size:9px">
                        <a href="https://github.com/adiralashiva8/robotframework-historic" target="_blank">robotframework-historic</a>
                    </p>
                </div>
            </div>
        </div>

        <div class="tabcontent" id="metrics">
            <h4><b><i class="fa fa-table"></i> Metrics</b></h4>
            <hr/>
            <table class="table table-striped table-bordered" id="sm">
                <thead>
                    <tr>
                        <th>Executed On</th>
                        <th>Total Tests</th>
                        <th>Passed Tests</th>
                        <th>Failed Tests</th>
                        <th>Duration</th>
                    </tr>
                </thead>
				<tbody>
					<suite_replace></suite_replace>
			   </tbody>
            </table>
        </div>
        <div class="tabcontent" id="test_metrics">
            <h4><b><i class="fa fa-table"></i> Test Metrics</b></h4>
            <hr/>
            <table class="table table-striped table-bordered" id="tm">
                <thead>
                    <tr>
                        <th>Executed On</th>
                        <th>Test Case</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Error Message</th>
                    </tr>
                </thead>
                <tbody>
                    <test_replace></test_replace>
                </tbody>
            </table>
        </div>
    </div>
    """
    return body

def get_html_footer():
    footer = """
            <script>
            function createBarGraph(tableID, column_0, column_1, column_2, limit, ChartID, label_1, label_2, label_3) {
                        var status = [];
                        css_selector_locator = tableID + ' tbody >tr'
                        var rows = $(css_selector_locator);
                        var columns;
                    
                        status.push([label_1, label_2, label_3]);
                        for (var i = 0; i < rows.length; i++) {
                            if (i == Number(limit)) {
                                break;
                            }
                            //status = [];
                            name_value = $(rows[i]).find('td');

                            col_0 = ($(name_value[Number(column_0)]).html()).trim();
                            col_1 = ($(name_value[Number(column_1)]).html()).trim();
                            col_2 = ($(name_value[Number(column_2)]).html()).trim();
                            status.push([col_0, parseFloat(col_1), parseFloat(col_2)]);
                        }
                        var data = google.visualization.arrayToDataTable(status);

                        var options = {
                            legend: 'none',
                            isStacked:true,
                            chartArea: {width: "95%",height: "85%"},
                            bar: {
                                groupWidth: '90%'
                            },
                            annotations: {
                                alwaysOutside: true,
                                textStyle: {
                                fontName: 'Comic Sans MS',
                                fontSize: 13,
                                bold: true,
                                italic: true,
                                color: "black",     // The color of the text.
                            },                        
                        },
                        hAxis: {
                            textStyle: {
                                fontName: 'Arial',
                                fontSize: 10,
                            }
                        },
                        series: {
                            0:{color:'#329932'},
                            1:{color:'#ff4c4c'}
                        },
                        vAxis: {
                            gridlines: { count: 10 },
                            textStyle: {                    
                                fontName: 'Comic Sans MS',
                                fontSize: 10,
                            }
                        },
                    };  

                        // Instantiate and draw the chart.
                        var chart = new google.visualization.ColumnChart(document.getElementById(ChartID));
                        chart.draw(data, options);
                    }
        </script>
        <script>
            function executeDataTable(tabname, sortCol) {
                        var fileTitle;
                        switch (tabname) {                        
                            case "#tm":
                                fileTitle = "TestMetrics";
                                break;
                            default:
                                fileTitle = "metrics";
                        }

                        $(tabname).DataTable({
                            retrieve: true,
                            "order": [
                                [Number(sortCol), "desc"]
                            ],
                            dom: 'l<".margin" B>frtip',
                            buttons: [
                                'copy', {
                                    extend: 'csv',
                                    filename: function() {
                                        return fileTitle + '-' + new Date().toLocaleString();
                                    },
                                    title: '',
                                }, {
                                    extend: 'excel',
                                    filename: function() {
                                        return fileTitle + '-' + new Date().toLocaleString();
                                    },
                                    title: '',                           
                                }, {
                                    extend: 'print',
                                    title: '',
                                },
                            ],
                        });
                    }
        </script>
        <script>
            function openPage(pageName, elmnt, color) {
                    var i, tabcontent, tablinks;
                    tabcontent = document.getElementsByClassName("tabcontent");
                    for (i = 0; i < tabcontent.length; i++) {
                        tabcontent[i].style.display = "none";
                    }
                    tablinks = document.getElementsByClassName("tablink");
                    for (i = 0; i < tablinks.length; i++) {
                        tablinks[i].style.backgroundColor = "";
                    }
                    document.getElementById(pageName).style.display = "block";
                    elmnt.style.backgroundColor = color;

                }
                // Get the element with id="defaultOpen" and click on it
                document.getElementById("defaultOpen").click();
        </script>
        <script>
            // Get the element with id="defaultOpen" and click on it
                document.getElementById("defaultOpen").click();
        </script>
        <script>
            $(window).on('load', function() {
                        $('.loader').fadeOut();
                    });
        </script>
    </body>
    """
    return footer

def get_and_create_suite_table_content(list_items):
    table_content = """
    <tr>
        <td align="center">execution_date</td>
        <td align="center">total_tests</td>
        <td align="center" style="color: green">passed_tests</td>
        <td align="center" style="color: red">failed_tests</td>
        <td align="center">duration</td>
    </tr>
    """
    table_content = table_content.replace("execution_date",list_items[0])
    table_content = table_content.replace("total_tests",list_items[1])
    table_content = table_content.replace("passed_tests",list_items[2])
    table_content = table_content.replace("failed_tests",list_items[3])
    table_content = table_content.replace("duration",list_items[4])
    
    return table_content

def get_and_create_test_table_content(list_items):
    t_table_content = """
    <tr>
        <td align="center">execution_date</td>
        <td>test_case</td>
        <td align="center">status</td>
        <td align="center">duration</td>
        <td>msg</td>
    </tr>
    """
    t_table_content = t_table_content.replace("execution_date",list_items[0])
    t_table_content = t_table_content.replace("test_case",list_items[1])
    t_table_content = t_table_content.replace("status",list_items[2])
    t_table_content = t_table_content.replace("duration",list_items[3])
    t_table_content = t_table_content.replace("msg",list_items[4])
    
    return t_table_content