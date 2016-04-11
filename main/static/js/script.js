// possible map filters:
// -- above a certain price
// -- below a certain price
// -- product type (would need to add this to scraper)
// -- by store type
// -- on sale

// big numbers:
// -- total unicorn stores
// -- total unicorn products
// -- total products in stores that day
// -- max price with product
// -- min price with product

var layer = new L.StamenTileLayer('toner-background')

var map = new L.Map('map').setView([41, -77.5], 7)
map.addLayer(layer)

var uniques = new Set()

// functionize this as makeUniques?
for (var i = 0; i < unicorns.length; i++) {
  var unicorn = unicorns[i]
  var unicorn_store_id = unicorn['store_id']

  storeAdded = false;
  if (!(unicorn_store_id in uniques) && storeAdded === false) {
    storeAdded = true
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

          product_info += '<div><strong>' +
            unicorn_name +
            '</strong>: ' +
            unicorn_bottles + (unicorn_bottles > 1 ? ' units' : ' unit') +
            ' // ' +
            unicorn_size +
            ' // ' +
            unicorn_price +
            ' // ' +
            on_sale + '</div>'
        }
      marker.bindPopup(popupHtml + product_info)
      }
    }
  }
});
