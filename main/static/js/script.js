var stores = []
var unicorns = []
var uniques = new Set()

var layer = new L.StamenTileLayer('toner-background')
var southWest = L.latLng(39, -81)
var northEast = L.latLng(44, -74)
var bounds = L.latLngBounds(southWest, northEast)
var map = new L.Map('map', {maxBounds: bounds, minZoom: 7, scrollWheelZoom: false})
    .setView([41, -77.5], 8)
    .locate({setView: true, maxZoom: 10})
map.addLayer(layer)
// listen for screen resize events
// window.addEventListener('load', function (e) {
//   // get the width of the screen after the resize event
//   var width = document.documentElement.clientWidth
//   // tablets are between 768 and 922 pixels wide
//   // phones are less than 768 pixels wide
//   if (width < 400) {
//     // set the zoom level to 10
//     map.minZoom(5)
//     map.setZoom(5)
//   } else {
//         // set the zoom level to 8
//     map.setZoom(8)
//   }
// })


function populateMap () {
  uniques.forEach(function (id) {
    for (var i = 0; i < stores.length; i++) {
      var store = stores[i];
      if (id === store['id']) {
        var store_address = store['address'];
        var storeLong = store['longitude'];
        var storeLat = store['latitude'];
        var store_phone = store['phone'];
        var store_type = store['store_type'];

        var marker = L.marker([storeLat, storeLong]).addTo(map);
        var popupHtml = '<h2>' + store_address + '</h2>';
        popupHtml += '<h4>' + store_type + ', ' + store_phone + '</h4>';

      var product_info = [];

      for (i = 0; i < unicorns.length; i++) {
        var unicorn = unicorns[i];
        if (unicorn['store_id'] === id) {
          var unicorn_name = unicorn['name'];
          var unicorn_bottles = unicorn['bottles'];
          var unicorn_size = unicorn['bottle_size'];
          var unicorn_price = '$' + unicorn['price'];
          var on_sale = unicorn['on_sale'] ? 'Sale price: $' + unicorn['on_sale'] : false;

          product_info += '<div><strong>' +
            unicorn_name +
            '</strong>: ' +
            unicorn_bottles + (unicorn_bottles > 1 ? ' units' : ' unit') +
            ' :: ' +
            unicorn_size +
            ' :: ' +
            unicorn_price
            if (on_sale) {
              + ' :: ' +
              on_sale + '</div>'
            } else {
              + ''
            }
        };
        marker.bindPopup(popupHtml + product_info, {maxWidth: 300, maxHeight: 250});
      }
      }
    }
  })
};

function secondAjax () {
  var stores_xhr = new XMLHttpRequest();
  stores_xhr.open('GET', 'https://s3.amazonaws.com/boozicorns/retail_stores-2016-04-10.json', true);
  stores_xhr.onload = function () {
    if (stores_xhr.status === 200) {
      stores = JSON.parse(stores_xhr.responseText);
      // better to do this through Django views because of the delay
      // in calculating it
      // var numStores = stores.length
      // document.getElementById('num-stores').innerHTML = numStores
      var stores_percentage = ((uniques.size / stores.length) * 100).toFixed(1);
      document.getElementById('boozicorns-stores-percentage').innerHTML = stores_percentage;
      populateMap()
    }
  };
  stores_xhr.send()
};

function firstAjax () {
  var unicorns_xhr = new XMLHttpRequest();
  unicorns_xhr.open('GET', 'https://s3.amazonaws.com/boozicorns/unicorns-' + scrapeDate + '.json', true);
  unicorns_xhr.onload = function () {
    if (unicorns_xhr.status === 200) {
      unicorns = JSON.parse(unicorns_xhr.responseText);
      var numBoozicorns = unicorns.length;
      document.getElementById('boozicorns').innerHTML = numBoozicorns.toLocaleString();
      for (var i = 0; i < unicorns.length; i++) {
        var unicorn = unicorns[i];
        var unicorn_store_id = unicorn['store_id'];
        if (!(unicorn_store_id in uniques)) {
          uniques.add(unicorn_store_id);
        }
      };
      var numBoozicornStores = uniques.size;
      document.getElementById('boozicorns-stores').innerHTML = numBoozicornStores;
      secondAjax()
    }
  }
  unicorns_xhr.send()
};

window.onload = firstAjax();

// var summary = document.getElementsByClassName('summary')
// var shown = false
//
// for (var i = 0; i < summary.length; i++) {
//   var data = summary[i]
//   if (!(shown)) {
//     data.onclick = function () {
//       data.style.display = 'inline-block'
//       shown = true
//     } else {
//       data.style.display = 'none'
//       shown = false
//     }
//   }
// }
