/* jslint browser:true */

var newsflash = require('./newsflash');

/**
 * Some next steps:
 *   X Build fake but representative JSON response from server.
 *   X Backbone model and view integration
 *   X Test out CSS animation and transition in sidebar
 *   X Populate models with serverside data
 *   - Productionize (gulp, mocha + chai, travis, maybe heroku?)
 */


window.addEventListener('load', function() {    
    // Instantiate a collection of Country's.
    var countries = new newsflash.CountryList();
    
    // Initialize a view for the map.
    var WorldMap = new newsflash.MapView({
        model: countries,
    });
    
    // Initialize a view for the sidebar.
    var CountrySidebar = new newsflash.CountrySidebarView({
        // Null country for starters. This needs to be replaced before
        // the sidebar is actually rendered.
        model: new newsflash.Country(),
    });
  
    // Initialize one Country object per path in the map.
    _.each(document.querySelectorAll('path'), function(el) {
        var country = new newsflash.Country({
            id: el.getAttribute('id'),
            name: el.getAttribute('title'),
            element: el,
        });
        
        countries.push(country);

        // Add click listeners to each country element.
        el.addEventListener('click', function(c) {
            return function() {
                CountrySidebar.model.set(c);
                document.querySelector('#sidebar').classList.add('active');  
            };
        }(country));        
    });
    
    // Fetch serverside data.
    // TODO: this should refresh periodically.
    countries.fetch({
        // Don't remove records that don't get an update; we still
        // want to have a full list of countries so that we can reference
        // them if need be.
        remove: false,
    });
});