
function myCharts(data){
    var myChart = echarts.init(document.getElementById('main'));
    option = {
        title : {
            text: data['title'],
        },
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data: data['legend'],
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        calculable : true,
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                data : data['xAxis']
            }
        ],
        yAxis : [
            {
                type : 'value'
            }
        ],
        series : [],
        dataZoom: {
            show: true,
            realtime: true,
            y: 36,
            height: 20,
            start: 20,
            end: 80
        },
    };

    ser = data['series'];
    for (var i in ser) { 
        dic = {
            name:i,
            type:'line',
            smooth:true,
            itemStyle: {normal: {areaStyle: {type: 'default'}}},
            data:ser[i]
        };
        option['series'].push(dic)
    }
    myChart.setOption(option);
}

function req_loan(loan_type){
     $.post("/ajax",{message: loan_type,web: 'loan'}, function(data,status){
        if(status == "success")
        {
            myCharts(data)
        }
        else
        {
            alert("Ajax 失败");
        }
    });
}