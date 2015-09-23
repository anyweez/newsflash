/**
 * Some next steps:
 *   X Build fake but representative JSON response from server.
 *   X Backbone model and view integration
 *   - Test out CSS animation and transition in sidebar
 *   X Populate models with serverside data
 *   - Productionize (gulp, mocha + chai, travis, maybe heroku?)
 */

var Country = Backbone.Model.extend({
    defaults: {
        id: null,
        name: null,
        element: null,
        // Marks whether we have data from the server on this country.
        // Will only be set by a proper server response.
        available: false,
    },
});

// A list of all countries, to be shared by the whole application.
var CountryList = Backbone.Collection.extend({
    model: Country,
    // Single endpoint to manage all countries and hotness scores.
    url: '/api',
    initialize: function() {
        _.bindAll(this, 'parse');
    },
    parse: function(response, options) {
        var self = this;
        
        // TODO: Set country.available back to false before this.
        _.each(response.countries, function(country) {
            // 'Available' flag gets set to true if this response included this
            // country, otherwise it should be false (including those who have been
            // included in the response in the past since that data may be stale.
            country.available = true;
            
            country.related_countries = _.map(country.related_countries, function(c) {
                var lookup = self.get(c.id);
                lookup.hotness = c.hotness;
                
                return lookup;
            });
        });
        return response.countries;
    },
});

window.addEventListener('load', function() {
    // Initialize the view
    var CountrySidebarView = Backbone.View.extend({
        el: '#sidebar',
        initialize: function() {
            _.bindAll(this, 'template', 'render');
            this.model.on('change', this.render);
        },
        // Rendering
        template: _.template(document.querySelector('#sidebar-template').innerHTML),
        render: function() {
            // TODO: Shouldn't have double-nested attributes here.
            var html = this.template(this.model.attributes.attributes);
            this.$el.html(html);
            
            document.querySelector('#close-sb').addEventListener('click', function() {
                document.querySelector('#sidebar').classList.remove('active');
                console.log('removing active');
            });
            
            return this;
        },
    });
    
    var MapView = Backbone.View.extend({
        el: '#map',
        initialize: function() {
            _.bindAll(this, 'render');
            this.model.on('change', this.render);
        },
        render: function() {
            console.log('rendering mapview');
            this.model.each(function(country) {
                if (country.attributes.available) {
                    var hotness = country.attributes.hotness.current;
                    // Paint the country based on what the current hotness value is.
                    if (hotness > 1.0) country.attributes.element.classList.add('heatmap-3');
                    else if (hotness > .65) country.attributes.element.classList.add('heatmap-2');
                    else if (hotness > .25) country.attributes.element.classList.add('heatmap-1');
                    else country.attributes.element.classList.add('heatmap-0');
                // If data isn't available, remove any classes that indicate that it
                // is available.
                } else {
                    country.attributes.element.classList.remove('heatmap-0');
                    country.attributes.element.classList.remove('heatmap-1');
                    country.attributes.element.classList.remove('heatmap-2');
                    country.attributes.element.classList.remove('heatmap-3');
                }
            });
        },
    });
    
    // Instantiate a collection of Country's.
    var countries = new CountryList();
    
    // Initialize a view for the map.
    var WorldMap = new MapView({
        model: countries,
    });
    
    // Initialize a view for the sidebar.
    var CountrySidebar = new CountrySidebarView({
        model: new Country(),
    });
  
    // Initialize one Country object per path in the map.
    var elements = document.querySelectorAll('path');
    _.each(elements, function(el) {
        var country = new Country({
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
            }
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