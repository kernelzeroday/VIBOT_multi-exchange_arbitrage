
// JS FOR MAIN SECTION
// initialize selects
document.addEventListener('DOMContentLoaded', () => {
  let elems = document.querySelectorAll('select');
  let instances = M.FormSelect.init(elems);
});

checkFormObjectValue = (selector) => {
  let formObject = document.querySelector(`${selector}`);
  let instanceFormObject = M.FormSelect.getInstance(formObject);
  let value = instanceFormObject.getSelectedValues();
  console.log(value)
  return value;
}
checkInputValue = (selector) => {
  let input = document.querySelector(`${selector}`);
  let inputValue = input.value;
  console.log(inputValue)
  return inputValue;
}
sendDataFromControls = (e) => {
  e.preventDefault();
  let gettedExchanges = checkFormObjectValue('#exchanges');
  let gettetPairs = checkFormObjectValue('#pairs');
  let gettedInput = checkInputValue('#input_controls1')
  console.log('gettedExchanges', gettedExchanges)
  console.log('gettetPairs', gettetPairs)
  console.log('gettedInput', gettedInput)
  let bodyToSend = {
    type: 'config',
    data: {
      min_treshold: gettedInput,
      exchanges: gettedExchanges,
      pairs: gettetPairs
    }
  }
  console.log('bodyToSend', JSON.stringify(bodyToSend))
  M.toast({html: 'Config is updating'}) // Its TEMPORARY SOLUTION !!!! NEED TO GO DOWN IN RESPONSE=> TAKE PROPERLY DATA AND DRAW
  fetch('Url To send', {
    method: 'post',
    headers: {
      "Content-type": "application/json"
    },
    body: JSON.stringify(bodyToSend)
  })
    .then(json)
    .then(function (data) {
      console.log('Request succeeded with JSON response', data);
      //TOAST NEED HERE
    })
    .catch(function (error) {
      console.log('Request failed', error);
    });

  
}
buttonsActs = (e) => {
  let target = event.target;
  let action = target.getAttribute('data-actionBtn');
  if (!action) return;
  console.log(action)
  fetch(`main_url/${action}`)
    .then(
      function (response) {
        if (response.status !== 200) {
          console.log('Looks like there was a problem. Status Code: ' +
            response.status);
          return;
        }
        response.json().then(function (data) {
          console.log(data);
        });
      }
    )
    .catch(function (err) {
      console.log('Fetch Error :-S', err);
    });
    M.toast({html: `You pushed the  ${action.toUpperCase()}`})
}

document.getElementById('send_btn').addEventListener('click', sendDataFromControls);
document.addEventListener('click', buttonsActs)
// JS FOR MAIN SECTION