// var today = new Date()
// var yesterday = new Date(today)
// yesterday.setDate(today.getDate() - 1)
// today = today.toISOString().slice(0, 10)
// yesterday = yesterday.toISOString().slice(0, 10)

var uniques = new Set()

var layer = new L.StamenTileLayer('toner-background')
var southWest = L.latLng(39, -81)
var northEast = L.latLng(44, -74)
var bounds = L.latLngBounds(southWest, northEast)
var map = new L.Map('map', {maxBounds: bounds, minZoom: 7}).setView([41, -77.5], 8).locate({setView: true, maxZoom: 10})
map.addLayer(layer)

for (var i = 0; i < unicorns.length; i++) {
  var unicorn = unicorns[i]
  var unicorn_store_id = unicorn['store_id']
  if (!(unicorn_store_id in uniques)) {
    uniques.add(unicorn_store_id)
  }
};

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

    var product_info = ''

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
});

// $.ajax({
//   async: true,
//   url: "unicorns-2016-04-17.json",
//   dataType: "json",
//   contentType: "charset=utf-8",
//   success: function(data) {
//     setting(data);
//   }
// });
//
// $.ajax({
//   async: true,
//   url: "data/stores/retail_stores-2016-04-10.json",
//   dataType: "json",
//   contentType: "charset=utf-8",
//   success: function(data) {
//     setting(data);
//   }
// });
