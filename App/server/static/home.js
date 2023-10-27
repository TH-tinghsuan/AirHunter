const oneWayBtn = document.getElementById('one-way-btn');
const returnBtn = document.getElementById('return-btn');
const returnDateLabel = document.getElementById('returnDateLabel');
const returnDateInput = document.getElementById('return_date');

scheduleSelect.addEventListener('change', function () {
    if (returnBtn.checked) {
        returnDateLabel.style.display = '';
        returnDateInput.style.display = '';
        returnDateInput.setAttribute("required", "true");
    } else if (oneWayBtn.checked) {
        returnDateLabel.style.display = 'none';
        returnDateInput.style.display = 'none';
        returnDateInput.removeAttribute("required");
    }
    else {
        returnDateLabel.style.display = 'none';
        returnDateInput.style.display = 'none';
        returnDateInput.removeAttribute("required");
    }
    });

const fromSelect = document.getElementById('from-selector');
const toSelect = document.getElementById('to-selector');

const fromOptions = {
    'TSA': ['台東豐年機場 TTT', '澎湖機場 MZG', '花蓮機場 HUN', '金門尚義機場 KNH', '馬祖(北竿)機場 MFK', '馬祖(南竿)機場 LZN'],
    'KHH': ['澎湖機場 MZG', '花蓮機場 HUN', '金門尚義機場 KNH'],
    'HUN': ['台中清泉崗機場 RMQ', '台北松山機場 TSA', '高雄小港國際機場 KHH'],
    'TTT': ['台北松山機場 TSA'],
    'TNN': ['澎湖機場 MZG', '金門尚義機場 KNH'],
    'RMQ': ['澎湖機場 MZG', '花蓮機場 HUN', '金門尚義機場 KNH'],
    'CYI': ['澎湖機場 MZG', '金門尚義機場 KNH'],
    'MZG': ['台中清泉崗機場 RMQ', '台北松山機場 TSA', '台南機場 TNN', '嘉義水上機場 CYI', '金門尚義機場 KNH', '高雄小港國際機場 KHH'],
    'KNH': ['台中清泉崗機場 RMQ', '台北松山機場 TSA', '台南機場 TNN', '嘉義水上機場 CYI', '澎湖機場 MZG', '高雄小港國際機場 KHH'],
    'MFK': ['台北松山機場 TSA'],
    'LZN': ['台中清泉崗機場 RMQ', '台北松山機場 TSA']
    };

fromSelect.addEventListener('change', () => {
    const fromSelectCategory = fromSelect.value;
    const toSelectOptions = fromOptions[fromSelectCategory] || [];
    toSelect.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.textContent = "請選擇";
    toSelect.appendChild(defaultOption);
    toSelectOptions.forEach((option) => {
        const newOption = document.createElement('option');
        newOption.textContent = option;
        newOption.value = option.slice(-3);
        toSelect.appendChild(newOption);
    });
});

const departDateInput = document.getElementById("depart_date")
var minDate = new Date();
var minDate_ts = minDate.getTime();
minDate.setTime(minDate_ts + 1 * 1000 * 60 * 60 *24);
var maxDate = new Date();
var maxDate_ts = maxDate.getTime();
maxDate.setTime(maxDate_ts + 60 * 1000 * 60 * 60 *24);
departDateInput.min = minDate.toISOString().split('T')[0];
departDateInput.max = maxDate.toISOString().split('T')[0];
returnDateInput.min = minDate.toISOString().split('T')[0];
returnDateInput.max = maxDate.toISOString().split('T')[0];
departDateInput.addEventListener("input", function() {
if (departDateInput.value === ''){
    returnDateInput.min = minDate.toISOString().split('T')[0];
    returnDateInput.max = maxDate.toISOString().split('T')[0];
    returnDateInput.value = '';
}
else if(departDateInput.value > returnDateInput.value){
    returnDateInput.value = '';
    returnDateInput.min = departDateInput.value;
}
else{
    returnDateInput.min = departDateInput.value;
}
});

fetch('/price/change/get')
.then(response => response.json())
.then(data => {
data.forEach(item => {
    const recommend_item = document.createElement("div")
    recommend_item.className = "recommend-item"
    const link = document.createElement("a")
    link.href = `/flight/lists?schedule=oneWay&departureAirports=${item.depart_airport_code}&arriveAirports=${item.arrive_airport_code}&departureDates=${item.depart_date}&returnDates=`

    const img_div = document.createElement("div")
    img_div.className = "recommend-img"
    const img = document.createElement("img")
    img.src = item.image
    img_div.appendChild(img)

    const detail = document.createElement("div")
    detail.className = "recommend-detail"
    const h3 = document.createElement('h3');
    h3.textContent = item.depart_airport + "-" + item.arrive_airport;

    const departDate = document.createElement('p');
    departDate.classList.add('depart-date');

    const dateSpan = document.createElement('span');
    dateSpan.textContent = item.depart_date;
    const departSpan = document.createElement('span');
    departSpan.textContent = '出發';
    departDate.appendChild(dateSpan);
    departDate.appendChild(departSpan);

    const todayPrice = document.createElement('p');
    todayPrice.classList.add('today-price');

    const todayPriceSpan = document.createElement('span');
    todayPriceSpan.textContent = '今日價格';
    const priceSpan = document.createElement('span');
    priceSpan.textContent = ' $ ' + item.today_price + " 起";
    todayPrice.appendChild(todayPriceSpan);
    todayPrice.appendChild(priceSpan);

    const describeText = document.createElement('p');
    describeText.classList.add('describe-text');
    const cheaperSpan = document.createElement('span');
    cheaperSpan.textContent = '比昨天便宜';
    const discountSpan = document.createElement('span');
    discountSpan.textContent = item.change_rate + "%";
    describeText.appendChild(cheaperSpan);
    describeText.appendChild(discountSpan);

    const recommend_list = document.querySelector(".recommend-item-list")
    const title = document.querySelector(".recommend-item-list-title")
    title.textContent = "最新國内機票優惠"
    detail.appendChild(h3);
    detail.appendChild(departDate);
    detail.appendChild(todayPrice);
    detail.appendChild(describeText);
    link.appendChild(img_div)
    link.appendChild(detail)
    recommend_item.appendChild(link)
    recommend_list.appendChild(recommend_item)
    })
})


function initMap(data) {
    const map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 25.0699, lng: 121.5525 }, // 台北松山機場的經緯度
        zoom: 7, // 設定初始縮放級別
    });
    data.forEach(item => {
            const airport_info = airports.find(airport => airport.name === item.arrive_airport);
            const marker = new google.maps.Marker({
                position: { lat: airport_info.lat, lng: airport_info.lng },
                map: map,
                title: airport_info.name
            });
            const link_href = `/flight/lists?schedule=oneWay&departureAirports=${item.depart_airport_code}&arriveAirports=${item.arrive_airport_code}&departureDates=${item.depart_date}&returnDates=`
            const infoWindow = new google.maps.InfoWindow({
                content: `<a href=${link_href}><p>${airport_info.name}</p><p>$ ${item.price}起</p></a>`
            });

            marker.addListener("click", () => {
                infoWindow.open(map, marker);
            });
        });
    }

// 建立機場資訊的陣列
const airports = [
   { name: "台北", lat: 25.0699, lng: 121.5525 },
   { name: "澎湖", lat: 23.4667, lng: 119.6194 },
   { name: "台中", lat: 24.2647, lng: 120.6200 },
   { name: "台東", lat: 22.7933, lng: 121.1817 },
   { name: "花蓮", lat: 24.0238, lng: 121.6179 },
   { name: "高雄", lat: 22.57182, lng: 120.34056 },
   { name: "金門", lat: 24.43615, lng: 118.368 },
   { name: "台南", lat: 22.94834, lng: 120.2162 },
   { name: "馬祖", lat: 26.2239, lng: 119.99931},
   { name: "馬祖(南竿)", lat: 26.158304, lng: 119.9562},
   { name: "嘉義", lat: 23.45477, lng: 120.403898},
   
];

fetch('/map/get')
.then(response => response.json())
.then(data => {
    initMap(data);
    const infoP = document.querySelector("#info-text")
    var dateSpan = document.createElement('span');
    dateSpan.textContent = data[0].depart_date;
    var searchSpan = document.createElement('span');
    searchSpan.textContent = '從台北出發的價格搜尋';
    infoP.appendChild(dateSpan);
    infoP.appendChild(searchSpan);
    data.forEach(item => { 
        const link_href = `/flight/lists?schedule=oneWay&departureAirports=${item.depart_airport_code}&arriveAirports=${item.arrive_airport_code}&departureDates=${item.depart_date}&returnDates=`
        const a_link = document.createElement("a")
        a_link.href = link_href

        var mapItemDiv = document.createElement('div');
        mapItemDiv.classList.add('map-item');
        var mapItemLeftDiv = document.createElement('div');
        mapItemLeftDiv.classList.add('map-item-left');
        var mapImg = document.createElement('img');
        mapImg.classList.add('map-img');
        mapImg.src = item.image;
        var mapFlightDetailDiv = document.createElement('div');
        mapFlightDetailDiv.classList.add('map-flight-detail');
        var cityH3 = document.createElement('h3');
        cityH3.textContent = item.arrive_airport;
        var flightInfoP = document.createElement('p');
        flightInfoP.textContent = item.depart_airport_code +" - "+ item.arrive_airport_code;

        mapItemLeftDiv.appendChild(mapImg);
        mapItemLeftDiv.appendChild(mapFlightDetailDiv);
        mapFlightDetailDiv.appendChild(cityH3);
        mapFlightDetailDiv.appendChild(flightInfoP);


        var mapItemRightDiv = document.createElement('div');
        mapItemRightDiv.classList.add('map-item-right', 'map-flight-detail');
        var trackButton = document.createElement('button');
        trackButton.textContent = '搜尋航班';
        var priceP = document.createElement('p');
        priceP.textContent = "$ " + item.price + " 起";

        mapItemRightDiv.appendChild(trackButton);
        mapItemRightDiv.appendChild(priceP);

        mapItemDiv.appendChild(mapItemLeftDiv);
        mapItemDiv.appendChild(mapItemRightDiv);

        a_link.appendChild(mapItemDiv)
        const infoDiv = document.querySelector("#info")
        infoDiv.appendChild(a_link);
    });
});