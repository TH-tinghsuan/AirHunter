const favList = document.getElementById("fav-list")
        fetch('/user/favorites/get')
            .then(response => response.json())
            .then(data => {
                if (data.length === 0){
                    wording = document.createElement("h2");
                    wording.textContent = "收藏清單裡目前沒有東西～～";
                    document.body.appendChild(wording);
                }
                else{
                    data.forEach(item => {
                        console.log(item)
                        const container = document.createElement("div");
                        container.id = "fav-item";
                        const text_container = document.createElement("div");
                        text_container.id = "fav-item-text";
                        
                        const info_container = document.createElement("div");
                        info_container.className = "text"
                        const depart_text = document.createElement("span");
                        const arrive_text = document.createElement("span");
                        const arrow = document.createElement("span");
                        depart_text.textContent = item.depart_city;
                        arrive_text.textContent = item.arrive_city;
                        if (item.schedule === "return"){arrow.textContent = "↔"}
                        else if (item.schedule === "oneWay"){arrow.textContent = "→"};
                        info_container.appendChild(depart_text)
                        info_container.appendChild(arrow)   
                        info_container.appendChild(arrive_text)
                        info_container.style.fontSize = "20px";
                        info_container.style.fontWeight = "bold";

                        const date_container = document.createElement("div");
                        date_container.className = "text"
                        const depart_date = document.createElement("span");
                        const return_date = document.createElement("span");
                        const dash_sign = document.createElement("span");
                        const schedule = document.createElement("span");
                        schedule.className = "schedule"
                        depart_date.textContent = item.depart_date_formatted;
                        date_container.appendChild(depart_date)
                        if (item.schedule === "return")
                            {
                                return_date.textContent = item.return_date_formatted;
                                dash_sign.textContent = "-"
                                schedule.textContent = "往返";
                                date_container.appendChild(dash_sign);
                                date_container.appendChild(return_date);
                                date_container.appendChild(schedule);
                            }
                        else if(item.schedule === "oneWay"){
                            schedule.textContent = "單程";
                            date_container.appendChild(schedule);
                        }
                        date_container.style.fontSize = "16px";
                        
                        const price_container = document.createElement("div");
                        price_container.className = "text";
                        const min_price = document.createElement("span");
                        min_price.textContent = `NTD$ ${item.min_price}`;
                        price_container.appendChild(min_price)
                        price_container.style.fontSize = "18px";

                        const link_container = document.createElement("div");
                        link_container.id = "fav-item-link"
                        
                        remove_fav_link = document.createElement("a")
                        remove_fav_link.href = '#'
                        remove_fav_link.id = "remove-fav"
                        remove_fav_img = document.createElement("img")
                        remove_fav_img.id = "remove-fav-img"
                        remove_fav_img.src = "https://side-project-flights-bucket.s3.ap-southeast-2.amazonaws.com/imgs/x-mark.png"
                        remove_fav_link.appendChild(remove_fav_img)
                        link_container.appendChild(remove_fav_link)
                        
                        detail_pg_link = document.createElement("a")
                        detail_pg_link.id = "link-detail"
                        if (item.schedule == "oneWay"){
                            detail_pg_link.href = `/flight/lists?schedule=${item.schedule}&departureAirports=${item.depart_airport_code}&arriveAirports=${item.arrive_airport_code}&departureDates=${item.depart_date}`
                        }
                        else if (item.schedule == "return"){
                            detail_pg_link.href = `/flight/lists?schedule=${item.schedule}&departureAirports=${item.depart_airport_code}&arriveAirports=${item.arrive_airport_code}&departureDates=${item.depart_date}&returnDates=${item.return_date}`
                        }
                        detail_pg_link.textContent = "檢視航班 →"
                        link_container.appendChild(detail_pg_link)
                
                        text_container.appendChild(info_container)
                        text_container.appendChild(date_container)
                        text_container.appendChild(price_container)
                        container.appendChild(text_container)
                        container.appendChild(link_container)
                        favList.appendChild(container)

                        remove_fav_img.addEventListener('click', function (event){
                            let data = {
                                schedule: item.schedule,
                                depart_date: item.depart_date,
                                return_date: item.return_date,
                                depart_airport_code: item.depart_airport_code,
                                arrive_airport_code: item.arrive_airport_code
                            }
                            console.log(data)
                            fetch('/user/favorites/remove', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify(data)
                                });  
                            container.style.display = 'none';
                        })
                    });
                }
            })
            .catch(error => {
                console.error('error occur:', error);
            });