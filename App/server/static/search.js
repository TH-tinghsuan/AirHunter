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