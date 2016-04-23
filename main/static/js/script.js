// var today = new Date()
// var yesterday = new Date(today)
// yesterday.setDate(today.getDate() - 1)
// today = today.toISOString().slice(0, 10)
// yesterday = yesterday.toISOString().slice(0, 10)

// don't want to have to manually update the number of stores in the intro text
// should it change with a new scrape for store data
var stores = []
var unicorns = []
var uniques = new Set()

var layer = new L.StamenTileLayer('toner-background')
var southWest = L.latLng(39, -81)
var northEast = L.latLng(44, -74)
var bounds = L.latLngBounds(southWest, northEast)
var map = new L.Map('map', {maxBounds: bounds, minZoom: 7, scrollWheelZoom: false}).setView([41, -77.5], 8).locate({setView: true, maxZoom: 10})
map.addLayer(layer)
// listen for screen resize events
window.addEventListener('load', function(e){
    // get the width of the screen after the resize event
    var width = document.documentElement.clientWidth;
    // tablets are between 768 and 922 pixels wide
    // phones are less than 768 pixels wide
    if (width < 400) {
        // set the zoom level to 10
        map.setZoom(9);

    } else {
        // set the zoom level to 8
        map.setZoom(8);
    }
});

function populateMap () {
  uniques.forEach(function (id) {
    for (i = 0; i < stores.length; i++) {
      var store = stores[i]
      if (id === store['id']) {
        store_address = store['address']
        storeLong = store['longitude']
        storeLat = store['latitude']
        store_phone = store['phone']
        store_type = store['store_type']

        var marker = L.marker([storeLat, storeLong]).addTo(map)
        var popupHtml = '<h2>' + store_address + '</h2>'
        popupHtml += '<h4>' + store_type + ', ' + store_phone + '</h4>'

      var product_info = []

      for (i = 0; i < unicorns.length; i++) {
        var unicorn = unicorns[i]
        if (unicorn['store_id'] === id) {
          var unicorn_name = unicorn['name']
          var unicorn_bottles = unicorn['bottles']
          var unicorn_size = unicorn['bottle_size']
          var unicorn_price = '$' + unicorn['price']
          var on_sale = unicorn['on_sale'] ? 'Sale price: $' + unicorn['on_sale'] : 'Not marked down'
          var data_date = unicorn['scrape_date']

          product_info += '<div><strong>' +
            unicorn_name +
            '</strong>: ' +
          //   data_date +
          //   ' // '
            unicorn_bottles + (unicorn_bottles > 1 ? ' units' : ' unit') +
            ' // ' +
            unicorn_size +
            ' // ' +
            unicorn_price +
            ' // ' +
            on_sale + '</div>'
        }
        marker.bindPopup(popupHtml + product_info, {maxWidth: 300, maxHeight: 250})
      }
      }
    }
  })
};

function secondAjax () {
  var stores_xhr = new XMLHttpRequest()
  stores_xhr.open('GET', 'https://s3.amazonaws.com/boozicorns/data/retail_stores-2016-04-10.json', true)
  stores_xhr.onload = function () {
    if (stores_xhr.status === 200) {
      stores = JSON.parse(stores_xhr.responseText)
      var numStores = stores.length
      document.getElementById('num-stores').innerHTML = numStores
   }
   populateMap()
  }
  stores_xhr.send()
};

function firstAjax () {
  var unicorns_xhr = new XMLHttpRequest()
  unicorns_xhr.open('GET', 'https://s3.amazonaws.com/boozicorns/data/unicorns-2016-04-19.json', true)
  unicorns_xhr.onload = function () {
    if (unicorns_xhr.status === 200) {
      unicorns = JSON.parse(unicorns_xhr.responseText)
      var numBoozicorns = unicorns.length
      document.getElementById('boozicorns').innerHTML = numBoozicorns.toLocaleString()
      for (var i = 0; i < unicorns.length; i++) {
        var unicorn = unicorns[i]
        var unicorn_store_id = unicorn['store_id']
        if (!(unicorn_store_id in uniques)) {
          uniques.add(unicorn_store_id)
        }
      }
      var numBoozicornStores = uniques.size
      document.getElementById('boozicorns-stores').innerHTML = numBoozicornStores
    }
    secondAjax()
  }
  unicorns_xhr.send()
};

window.onload = firstAjax()

    // stores_xhr.onload = function() {
    //     if (stores_xhr.status === 200) {
    //         stores = JSON.parse(stores_xhr.responseText)
    //     }
    //     var numStores = stores.length
    //     document.getElementById('num-stores').innerHTML = numStores
    //     return stores
    // }
    // stores_xhr.send()
