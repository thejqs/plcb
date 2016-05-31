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

var width = document.documentElement.clientWidth;

var summary = Array.from(document.getElementsByClassName('summary'));
var dive = Array.from(document.getElementsByClassName('unicorn-dive'));

dive.forEach(function (v, idx) {
  var shown = false;
  summary[idx].addEventListener('click', function(e) {
    e.preventDefault();

    if (v && !(shown)) {
      shown = true;
      console.log(shown)
      v.style.display = 'inline-block';
      return;
    } else if (v && shown) {
      shown = false;
      console.log(shown)
      v.style.display = 'none';
      return;
    }
    console.log(shown)
  })
})

// listen for screen resize
window.addEventListener('load', function(e) {
  // get screen width after resize
  if (width < 450) {
    map.minZoom(6);
    map.setZoom(6);
  } else {
    map.setZoom(8);
  }
});


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
        var popupHtml = '<h2>' +
                        store_address +
                        '</h2>';
        popupHtml += '<h4>' +
                     store_type +
                     ', ' +
                     store_phone +
                     '</h4>';

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
        marker.bindPopup(popupHtml + product_info, {maxWidth: 250, maxHeight: 250});
      }
      }
    }
  })
};

function secondAjax () {
  var stores_xhr = new XMLHttpRequest();
  stores_xhr.open('GET', 'https://s3.amazonaws.com/boozicorns/retail_stores-2016-05-28.json', true);
  stores_xhr.onload = function () {
    if (stores_xhr.status === 200) {
      getStores(stores_xhr);
      populateMap();
    };
  };
  stores_xhr.send()
};

function firstAjax () {
  var unicorns_xhr = new XMLHttpRequest();
  unicorns_xhr.open('GET', 'https://s3.amazonaws.com/boozicorns/unicorns-' + scrapeDate + '.json', true);
  unicorns_xhr.onload = function () {
    if (unicorns_xhr.status === 200) {
      getUnicorns(unicorns_xhr);
      secondAjax();
    }
  }
  unicorns_xhr.send()
};

function getUnicorns(unicorns_xhr) {
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
};

function getStores(stores_xhr) {
  stores = JSON.parse(stores_xhr.responseText);
  // better to do this through Django views because of the delay
  // in calculating it:
  // var numStores = stores.length
  // document.getElementById('num-stores').innerHTML = numStores
  var stores_percentage = ((uniques.size / stores.length) * 100).toFixed(1);
  document.getElementById('boozicorns-stores-percentage').innerHTML = ', ' + stores_percentage + '% of total';
};

window.onload = firstAjax();
