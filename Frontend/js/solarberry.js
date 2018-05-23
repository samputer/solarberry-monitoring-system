//
//                       \ | /
//                     '-.;;;.-'
//                    -==;;;;;==-
//                     .-';;;'-.
//                       / | \
//                         '
//  _____       _           ______
// /  ___|     | |          | ___ \
// \ `--.  ___ | | __ _ _ __| |_/ / ___ _ __ _ __ _   _
//  `--. \/ _ \| |/ _` | '__| ___ \/ _ \ '__| '__| | | |
// /\__/ / (_) | | (_| | |  | |_/ /  __/ |  | |  | |_| |
// \____/ \___/|_|\__,_|_|  \____/ \___|_|  |_|   \__, |
// Solarberry Monitoring System                    __/ |
// by Sam Gray, 2018                              |___/
//
// SolarBerry Monitoring System   Copyright (C) 2018  Sam Gray - www.sagray.co.uk
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

// Solarberry Javascript
var docready = false;
var readytoroll = false;
var graph1data = [
    ['x'],
    ['temperature_c'],
    ['irradiance'],
    ['voltage_out'],
    ['voltage_in'],
    ['battery_percent'],
    ['current_in'],
    ['current_out']
];
var graph1;
var graph2data = [
    ['x'],
    ['temperature_c'],
    ['irradiance'],
    ['voltage_out'],
    ['voltage_in'],
    ['battery_percent'],
    ['current_in'],
    ['current_out']
];
var graph2;

var sevensegcolours = {
    'error': {
        'on': '#ff0000',
        'off': '#320000'
    },
    'danger': {
        'on': '#ff0000',
        'off': '#320000'
    },
    'ok': {
        'on': '#00ff00',
        'off': '#003200'
    },
    'warning': {
        'on': '#fffc00',
        'off': '#323100'
    },
}

var ws;

// http://stackoverflow.com/questions/5560248/programmatically-lighten-or-darken-a-hex-color-or-rgb-and-blend-colors
    function blendColors(c0, c1, p) {
        var f = parseInt(c0.slice(1), 16),
            t = parseInt(c1.slice(1), 16),
            R1 = f >> 16,
            G1 = f >> 8 & 0x00FF,
            B1 = f & 0x0000FF,
            R2 = t >> 16,
            G2 = t >> 8 & 0x00FF,
            B2 = t & 0x0000FF;
        return "#" + (0x1000000 + (Math.round((R2 - R1) * p) + R1) * 0x10000 + (Math.round((G2 - G1) * p) + G1) * 0x100 + (Math.round((B2 - B1) * p) + B1)).toString(16).slice(1);
    }



// For the 7 seg displays
$(document).ready(function() {
    // Kick off the loading animations
    $('#graph2_container').LoadingOverlay("show");
    $('#graph1_container').LoadingOverlay("show");

    console.log("ready!");
    $(".lcd").sevenSeg({ digits: 4, value: 0000, colorOff: "#003200", colorOn: "Lime", });

    $(".chartswitcher_l").click(function() {
        // Selected one of the durations
        $('#graph2_container').LoadingOverlay("show");

        $('.chartswitcher_l').removeClass('active');
        $('.chartswitcher_l').removeClass('disabled');
        $('.chartswitcher_l').addClass('active');
        $(this).removeClass('active');
        $(this).addClass('disabled');

        selected_duration = $('.chartswitcher_l.disabled').val();
        selected_method = $('.chartswitcher_r.disabled').val();

        console.log(selected_duration);
        console.log(selected_method);

        json_to_send = {
            "duration": selected_duration,
            "method": selected_method
        }
        ws.send(JSON.stringify(json_to_send));
        
    });

    $(".chartswitcher_r").click(function() {
        // Selected one of the durations
        $('#graph2_container').LoadingOverlay("show");
        $('.chartswitcher_r').removeClass('active');
        $('.chartswitcher_r').removeClass('disabled');
        $('.chartswitcher_r').addClass('active');
        $(this).removeClass('active');
        $(this).addClass('disabled');

        selected_duration = $('.chartswitcher_l.disabled').val();
        selected_method = $('.chartswitcher_r.disabled').val();

        console.log(selected_duration);
        console.log(selected_method);

        json_to_send = {
            "duration": selected_duration,
            "method": selected_method
        }
        ws.send(JSON.stringify(json_to_send));
        
    });

    // $(".chart2update").click(function() {
    //     if ($(this).hasClass("active")) {

    //         $(.chartswitcher_l).removeClass('active');
    //         $(.chartswitcher_r).removeClass('active');


    //         $(this).removeClass('active');
    //         $(this).addClass('disabled');

    //         selected_duration = $('.chartswitcher_l.disabled').val();
    //         selected_method = $('.chartswitcher_r.disabled').val();

    //         console.log(selected_duration);
    //         console.log(selected_method);

    //         json_to_send = {
    //             "duration": selected_duration,
    //             "method": selected_method
    //         }
    //         ws.send(JSON.stringify(json_to_send));


    //         $('.chart2update').removeClass("active");
    //         $('.chart2update').removeClass("disabled");
    //         $('.chart2update').addClass("active");

    //         $("[value='"+selected_method+"']").removeClass('active');
    //         // $("[value='"+selected_duration+"']").removeClass('active');

    //         $("[value='"+selected_method+"']").addClass('disabled');
    //         // $("[value='"+selected_duration+"']").addClass('disabled');


    //         // $('.chart2update').addClass("active");
    //         // $("[value='"+selected_method+"']").addClass('disabled');
    //         // $("[value='"+selected_duration+"']").addClass('disabled');
    //         console.log(json_to_send);
    //         // ws.send(JSON.stringify(json_to_send));
    //         $('#graph2_container').LoadingOverlay("show");

    //     } else {
    //         console.log('Button is disabled');
    //     }
    // });

});

// graph stuff
$(document).ready(function() {
    console.log("init graphs");

    graph1 = c3.generate({
        bindto: '#graph1_container',
        data: {
            x: 'x',
            format: '%H:%M:%S',
            xFormat: '%Y-%m-%dT%H:%M:%S.%LZ',
            columns: graph1data,
            types: {
                temperature_c: 'line',
                irradiance: 'line'
            },
            axes: {
                irradiance: 'y2'
            }
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    format: '%H:%M:%S'
                }
            },
            y: {
                show: false
            }
        }
    });


    graph2 = c3.generate({
        bindto: '#graph2_container',
        data: {
            x: 'x',
            format: '%Y-%m-%dT%H:%M:%S',
            xFormat: '%Y-%m-%dT%H:%M:%S.%LZ',
            columns: graph2data,
            types: {
                temperature_c: 'line',
                irradiance: 'line'
            },
            axes: {
                irradiance: 'y2'
            }
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    format: '%Y-%m-%d %H:%M:%S'
                }
            },
            y: {
                show: false
            }
        }
    });

});


function date_time(id, startdate) {
    var servertimestamp = Date.parse(startdate);
    date = new Date(servertimestamp);
    year = date.getFullYear();
    month = date.getMonth();
    months = new Array('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December');
    d = date.getDate();
    day = date.getDay();
    days = new Array('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday');
    h = date.getHours();
    if (h < 10) {
        h = "0" + h;
    }
    m = date.getMinutes();
    if (m < 10) {
        m = "0" + m;
    }
    s = date.getSeconds();
    if (s < 10) {
        s = "0" + s;
    }
    result = '' + days[day] + ' ' + months[month] + ' ' + d + ' ' + year + ', ' + h + ':' + m + ':' + s;
    document.getElementById(id).innerHTML = result;
    date.setSeconds(date.getSeconds() + 1);
    setTimeout('date_time("' + id + '","' + date + '");', '1000');
    return true;
}


function configure_websocket(){
        // Here's the important stuff - websockets

    ws = new WebSocket("ws://localhost:5678/"),
        messages = document.createElement('ul');

    ws.onopen = function() {
        // Web Socket is connected, send data using send()
        $('#websocket_status').html('Connection Status: <span class="label label-success">Connected</span>');
        $('body').css("background-color", "#ffffff");
        console.log("Alerting server that we're ready to receive the initial data");
        ws.send(JSON.stringify({'ready':true}));
    };

    ws.onclose = function() {
        $('#websocket_status').html('Connection Status: <span class="label label-danger">Disconnected</span>');
        $('.lcd').sevenSeg({ value: 000 });
        $('body').css("background-color", "#ffc6c6");
    };

    ws.onmessage = function(event) {
        var indata = event.data;
        var json_data = JSON.parse(indata);

        console.log(json_data);
        for (var key in json_data) {
            if ((key == 'initial')) {
                console.log("Received the initial setup data - Processing it...");
                // ***** Take a timestamp from the initial data and use it to set the time on the page (Server time!) *****
                date_time('date_time', json_data[key]);

                // TODO - Reenable this

                // ***** Use the 'config' section to log some of our query frequencies
//                for (var i = json_data['config'].length - 1; i >= 0; i--) {
//                    if ($('#' + json_data['config'][i]['category'] + '_frequency').length) {
//                        $('#' + json_data['config'][i]['category'] + '_frequency').html('Query Frequency: every ' + json_data['config'][i]['frequency'] + ' seconds');
//                    }
//                }


                for (var metric in json_data){
                    console.log(metric);
                }

                // ***** Now you have a bunch of metrics arriving as the payload, loop through themf and do the needful
                for (var metric in json_data) {
                    console.log("Received initial " + metric + " data");
                    var snapshot = json_data[metric];
                    //Whilst running locally, this breaks things, can just uncomment as soon as prod
                    // ***** Temperature
                    // if (metric == 'temperature_c') {
                    //     snapshotsJSON = JSON.parse(snapshot);
                    //     $('#thermometer').thermometer('setValue', 100);
                    // }

                    // ***** Graph 1
                    if (metric == 'graph1') {
                        console.log("Got graph1 data");
                        console.log(snapshot)
                        snapshotsJSON = (snapshot);
                        // // Get all of the snapshots within the block and process them one by one
                        for (var snapshot_index in snapshotsJSON) {

                        // //     // ***** Update graph1 with each snapshot
                            var entry = snapshotsJSON[snapshot_index];
                            process_graph1(entry, false);
                        }
                    }

                    else if (metric != 'initial'){
                        console.log(metric)
                        snapshotsJSON = JSON.parse(snapshot);
                        metric_value = snapshotsJSON[snapshotsJSON.length-1]['value'];
                        level = snapshotsJSON[snapshotsJSON.length-1]['level'];
                                                console.log(metric_value)
                        console.log(level);
                        // TODO - Make these fade-in again
                        $('#' + metric).sevenSeg({ value: metric_value });
                        $('#' + metric + ' .sevenSeg-segOn').css('fill', sevensegcolours[level]['on']);
                        $('#' + metric + ' .sevenSeg-svg').css('fill', '"' + sevensegcolours[level]['off'] + '"');
                    }

                   // else if (metric != 'initial'){
                   //     console.log("***"+metric);
                   //     snapshotsJSON = JSON.parse(snapshot);
                   //     // console.log(snapshotsJSON[snapshotsJSON.length-1]);
                   //     metric_value = snapshotsJSON[snapshotsJSON.length-1]['value'];
                   //     level = snapshotsJSON[snapshotsJSON.length-1]['level'];
                   //
                   //     console.log(snapshotsJSON);
                   //
                   //     if (metric_value != undefined){
                   //         $('#' + metric).fadeOut('fast', function() {
                   //         $('#' + metric).sevenSeg({ value: metric_value });
                   //
                   //         // console.log(level)
                   //
                   //         $('#' + metric + ' .sevenSeg-segOn').css('fill', sevensegcolours[level]['on']);
                   //         $('#' + metric + ' .sevenSeg-svg').css('fill', '"' + sevensegcolours[level]['off'] + '"');
                   //         $('#' + metric).fadeIn('fast');
                   //      });
                   //     }
                   //     }
//                        console.log(json_data[metric].length);
//                        console.log(json_data[metric]);
//                        if (json_data[metric] != undefined){
//                        json_data = JSON.parse(json_data[metric]);
////                        console.log(json[(json.length)-1]);
//                        $('#' + metric).fadeOut('fast', function() {
//                        $('#' + metric).sevenSeg({ value: json_data[(json_data.length)-1]['value'] });
//                        // console.log('#'+json_data['metric']+'> .sevenSeg-segOn');
//                        $('#' + metric + ' .sevenSeg-segOn').css('fill', sevensegcolours[json_data['level']]['on']);
//                        $('#' + metric + ' .sevenSeg-svg').css('fill', '"' + sevensegcolours[json_data['level']]['off'] + '"');
//                        $('#' + metric).fadeIn('fast')
//                    });
//                    }

                }
                $('#graph1_container').LoadingOverlay("hide");
                $('#graph2_container').LoadingOverlay("hide");

                readytoroll = true; // This tells the rest of the app that we can start processing snapshots now
                // Didn't realise you could style console output! That's cool! (it's been a long day...)
                console.log("%cWe're now receiving LIVE data :-D %cWooHoo!","color:green; font-weight:bold","color:orange;font-weight:bold")

                break;
            } 
            else if (key == 'response') {
                console.log("Received a response to our graph2 request");
                graph2data = [
                    ['x'],
                    ['temperature_c'],
                    ['irradiance'],
                    ['voltage_out'],
                    ['voltage_in'],
                    ['battery_percent'],
                    ['current_in'],
                    ['current_out']]
                var json = JSON.parse(json_data['SQL'])
                for (var entry in json){
                    var current_item = json[entry];
                    // // Add the timestamp to the x axis
                    graph2data[0].push(new Date(current_item["timestamp"]).toISOString());
                    // Find out where to add the value
                    var index = 1;
                    if(current_item['metric'] == 'temperature_c'){index = 1;
                        console.log(current_item['value']);
                    }
                    else if(current_item['metric'] == 'irradiance'){index = 2;}
                    else if(current_item['metric'] == 'voltage_out'){index = 3;}
                    else if(current_item['metric'] == 'voltage_in'){index = 4;}
                    else if(current_item['metric'] == 'battery_percent'){index = 5;}
                    else if(current_item['metric'] == 'current_in'){index = 6;}
                    else if(current_item['metric'] == 'current_out'){index = 7;}
                    // Add each of the values
                    graph2data[index].push(current_item['value']);

                }

                // Refresh the graph
                graph2.load({
                    columns: graph2data
                });

                $('#graph2_container').LoadingOverlay("hide");

            }
            else if (json_data.hasOwnProperty(key)) {
                // console.log("Received a data snapshot");
                // ***** Change all of the data on the status bar at the top *****
                // Fade out the existing sevenseg, change the data, and fade it back in as part of the callback
                // Also set the colours based on the severity - defined at the top
                if ($('#' + json_data['metric']).length) {
                    $('#' + json_data['metric']).fadeOut('fast', function() {
                        $('#' + json_data['metric']).sevenSeg({ value: json_data['value'] });
                        console.log()
                        // console.log('#'+json_data['metric']+'> .sevenSeg-segOn');
                        $('#' + json_data['metric'] + ' .sevenSeg-segOn').css('fill', sevensegcolours[json_data['level']]['on']);
                        $('#' + json_data['metric'] + ' .sevenSeg-svg').css('fill', '"' + sevensegcolours[json_data['level']]['off'] + '"');
                        $('#' + json_data['metric']).fadeIn('fast')
                    });
                }
                // ***** Do what we need to do for temperature *****
                if ((key == 'metric') && (json_data[key] == 'temperature_c')) {
                    $('#thermometer').thermometer('setValue', json_data['value']);
                }

                if ((key == 'metric') && (json_data[key] == 'graph1') && readytoroll) {
                    var entry = json_data
                    process_graph1(entry, true);
                }
            }
            else {
                console.log("Received a message that I didn't understand!");
            }
        }
    };

}


$(document).ready(function() {
    
    console.log("init Thermometer");
    $('#thermometer').thermometer({
                        startValue: 0,
                        height: 180,
                        width: "100%",
                        bottomText: "-10°C",
                        topText: "45°C",
                        animationSpeed: 500,
                        maxValue: 45,
                        minValue: -10,
                        pathToSVG: 'vendor/thermometer/svg/thermo-bottom.svg',
                        liquidColour: function(value) {
                            return blendColors("#0024FF", "#FF0000", value / 55);
                        },
                        valueChanged: function(value) {
                            $('#thermovalue').css("color", blendColors("#0024FF", "#FF0000", value / 55));
                            $('#thermovalue').text(value.toFixed(2) + '°C');
                        }
                    });

    console.log("configuring websocket");
    //This also uses the connect callback to let the server know we're ready for data, it is the last thing we do.
    configure_websocket();

});




function process_graph1(entry, scroll) {
    // entry = JSON.parse(entry);
    console.log(entry);
    graph1data[0].push(new Date(entry["timestamp"]).toISOString());
    graph1data[1].push(entry['value']["temperature_c"]["value"]);
    graph1data[2].push(entry["value"]["irradiance"]["value"]);
    graph1data[3].push(entry["value"]["voltage_out"]["value"]);
    graph1data[4].push(entry["value"]["voltage_in"]["value"]);
    graph1data[5].push(entry["value"]["battery_percent"]["value"]);
    graph1data[6].push(entry["value"]["current_in"]["value"]);
    graph1data[7].push(entry["value"]["current_out"]["value"]);

    if (scroll) {
        for (var i = graph1data.length - 1; i >= 0; i--) {
            graph1data[i].splice(1, 1); // The first entry is the dataset name, so remove the 2nd
        }
    }
    graph1.load({
        columns: graph1data
    });
}
