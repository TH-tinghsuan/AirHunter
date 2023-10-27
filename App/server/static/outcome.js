var items = document.querySelectorAll('#item');
        items.forEach(function(item) {
            item.addEventListener('click', function() {
                var agentInfo = item.querySelector('#price-info'); 
                if (agentInfo.style.display === 'block') {
                    agentInfo.style.display = 'none';
                } else {
                    agentInfo.style.display = 'block';
                }
            });
        });

        var currentURL = window.location.href;
        var url = new URL(currentURL);
        var schedule = url.searchParams.get("schedule");
        var departureAirports = url.searchParams.get("departureAirports").toUpperCase();
        var arriveAirports = url.searchParams.get("arriveAirports").toUpperCase();
        var departureDates = url.searchParams.get("departureDates");
        var returnDates = url.searchParams.get("returnDates");

        var direct_btn = document.querySelectorAll('.direct-btn');
        direct_btn.forEach(function(button){
            button.addEventListener('click', function(){
                $.blockUI({
                            message: '<img id="direct-img" src="https://side-project-flights-bucket.s3.ap-southeast-2.amazonaws.com/imgs/plane.gif"> </br> <p>正在為您導向至旅行社....</p> ' ,
                            css: {
                                border: 'none',
                                padding: '15px',
                                backgroundColor: '#000',
                                '-webkit-border-radius': '10px',
                                '-moz-border-radius': '10px',
                                opacity: .5,
                                color: '#000000',
                                backgroundColor: '#FFFFFF'
                                
                            }  ,
                            onBlock: null, 
                            onUnblock: null 
                        });
                        setTimeout(function () {
                            $.unblockUI(); 
                        }, 10000);
                var id = button.id.split("-")
                var request_data;
                if (schedule === "return")  {
                    var agentName = id[0]
                    var d_flightCode = id[1]
                    var r_flight_code = id[2]
                    request_data = {
                        schedule: schedule,
                        agent_name: agentName, 
                        start_date: departureDates, 
                        return_date: returnDates, 
                        depart_at: departureAirports, 
                        return_at: arriveAirports, 
                        d_flight_code: d_flightCode, 
                        r_flight_code: r_flight_code
                        }
                }
                else if (schedule === "oneWay"){
                    var agentName = id[0]
                    var flightCode = id[1]
                    request_data = {
                        schedule: schedule,
                        agent_name: agentName, 
                        start_date: departureDates, 
                        return_date: returnDates, 
                        depart_at: departureAirports, 
                        return_at: arriveAirports, 
                        d_flight_code: flightCode, 
                        r_flight_code: null
                        }
                }
                
                var getUrls = {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(request_data)
                    }

                fetch('/flight/agentUrl/get', getUrls)
                    .then(function(response) {
                        if (!response.ok) {
                            throw new Error('Server response error');
                            }
                        return response.json(); 
                    })
                    .then(function(data){
                        var direct_url = data.url
                        window.location.href = direct_url;
                    });
                });
        });

        var far_btn = document.getElementById('favoriteBtn');
        far_btn.addEventListener('click', function() {
            var minPriceText = document.querySelectorAll('#item')[0].querySelector('#min-price').textContent;
            var matches = minPriceText.match(/\d+/);
            if (matches) {
                    var minPrice = parseInt(matches[0], 10);
                } else {
                    var minPrice = null; 
                }

            let data = {};
            if (schedule === "oneWay") {
                data = {
                    schedule: "oneWay",
                    departAirport: departureAirports,
                    arriveAirport: arriveAirports,
                    departDate: departureDates,
                    returnDates: null,
                    minPrice: minPrice
                }
            }
            else if (schedule === "return") {
                data = {
                    schedule: "return",
                    departAirport: departureAirports,
                    arriveAirport: arriveAirports,
                    departDate: departureDates,
                    returnDates: returnDates,
                    minPrice: minPrice
                }
            }

            fetch('/user/favorites/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })       
            swal("已為您追蹤票價！", "當最低價格變動時，將以e-mail通知", "success");
        });