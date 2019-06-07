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

    def start_suite(self, name, attrs):
        self.test_count = len(attrs['tests'])

    def end_test(self, name, attrs):
        if self.test_count != 0:
            self.total_tests += 1
        
        if attrs['status'] == 'PASS':
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def close(self):
        self.end_time = datetime.datetime.now().time().strftime('%H:%M:%S')
        self.total_time=(datetime.datetime.strptime(self.end_time,'%H:%M:%S') - datetime.datetime.strptime(self.start_time,'%H:%M:%S'))

        # Connect to db, if db doesn't exist create new one
        self.con = sql_connection()
        sql_table(self.con)

        entities = (str(self.date_now), str(self.total_tests), str(self.passed_tests), str(self.failed_tests), str(self.total_time))
        sql_insert(self.con, entities)
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

def sql_connection():
    try: 
        con = sqlite3.connect('historical_results_do_not_delete.db')
        return con 
    except Error: 
        print(Error)

def sql_table(con): 
    cursorObj = con.cursor()
    try:
        cursorObj.execute("CREATE TABLE IF NOT EXISTS results(execution_date text, total_tests text, passed_tests text, failed_tests text, duration text)") 
        con.commit()
    except Error:
        print(Error)

def sql_insert(con, entities):
    cursorObj = con.cursor()
    cursorObj.execute('INSERT INTO results(execution_date, total_tests, passed_tests, failed_tests, duration) VALUES(?, ?, ?, ?, ?)', entities)
    con.commit()

def generate_html_report(con): 

    head = get_html_head_text()
    body = get_html_body()    
    script = get_html_footer()
    table_content = ""

    cursorObj = con.cursor() 
    cursorObj.execute('SELECT * FROM results') 
    rows = cursorObj.fetchall() 
    for row in rows:
        table_content += add_and_get_table_content(row)

    historical_results_file = open('HistoricResults.html','w')
    table_content_html = "<tbody>" + str(table_content) + "</tbody></table></div>"
    page_content = str(head) + str(body) +  str(table_content_html) + str(script)
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
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/vfs_fonts.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.html5.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.print.min.js" type="text/javascript"></script>
        <style>
            body { font-family: -apple-system, sans-serif; }            
            .main { padding-top: 10px; }
            th, td { width: 20% }            
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
        <div class="main col-md-12"> 
        <div class="tabcontent" id="metrics">			
			<div class="d-flex flex-column flex-md-row align-items-center p-1 mb-3 bg-light border-bottom shadow-sm">                
                <div class="col-md-12" style="background-color:white;height:350px;width:auto;border:groove;">
                    <span style="font-weight:bold">Latest 10 Results Trend</span>
                    <div id="testsBarID" style="height:300px;width:auto;"></div>
                </div>
            </div>
            <script>
            window.onload = function(){
                executeDataTable('#tm',0);
                createBarGraph('#tm', 0, 2, 3, 10, 'testsBarID', 'Executed On', 'Pass', 'Fail')
            };
            </script>        
            <hr/>
            <table class="table table-striped table-bordered" id="tm">
                <thead align="center">
                    <tr>
                        <th>Executed On</th>
                        <th>Total</th>
                        <th>Pass</th>
                        <th>Fail</th>
                        <th>Duration</th>
                    </tr>
                </thead>
    """
    return body

def get_html_footer():
    footer = """
            <div class="row">
                <div class="col-md-12" style="height:25px;width:auto;">
                    <p class="text-muted" style="text-align:center;font-size:9px">
                        <a href="https://github.com/adiralashiva8/robotframework-historic" target="_blank">robotframework-historic</a>
                    </p>
                </div>
            </div>
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
                $(window).on('load', function() {
                    $('.loader').fadeOut();
                });
            </script>
    </body>
    """
    return footer

def add_and_get_table_content(list_items):
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