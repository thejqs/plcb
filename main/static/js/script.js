var layer = new L.StamenTileLayer('toner-background');

var map = new L.Map('map').setView([41, -77], 8);
map.addLayer(layer);

var uniques = new Set()

for (var i = 0; i < unicorns.length; i++) {
  var unicorn = unicorns[i];
  var unicorn_store_id = unicorn['store_id'];

  storeAdded = false;
  if (!(unicorn_store_id in uniques) && storeAdded === false) {
    storeAdded = true;
    uniques.add(unicorn_store_id);
  }
};

uniques.forEach(function (id) {
    for (i = 0; i < stores.length; i++) {
      var store = stores[i]
      if (id === store['id']) {
      store_address = store['address'];
      storeLong = store['longitude'];
      storeLat = store['latitude'];
      store_phone = store['phone'];
      store_type = store['store_type'];

      var marker = L.marker([storeLat, storeLong]).addTo(map);
      var popupHtml = '<h2>' + store_address + '</h2>';
      popupHtml += '<h4>' + store_type + ', ' + store_phone + '</h4>';
    //   popupHtml += '<div>'  + '</div>';

      for (i = 0; i < unicorns.length; i++) {
        var unicorn = unicorns[i];
        if (unicorn['store_id'] === id) {
          var unicorn_name = unicorn['name'];
          var unicorn_bottles = unicorn['bottles'];
          var unicorn_price = unicorn['price'];
          var on_sale = unicorn['on_sale']

          popupHtml += '<div>' + unicorn_name + ': ' + unicorn_bottles + ' // ' + unicorn_price + ' // ' + on_sale  + '</div>';
        //   popupHtml += '<div>' + unicorn_bottles + ' // ' + unicorn_price + ' // ' + on_sale + '</div>';
        //   popupHtml += '<div>' + unicorn_price + '</div>';
        //   popupHtml += '<div>' + on_sale + '</div>'
      }
      marker.bindPopup(popupHtml);
    }
  }
}
});
