/**
 * Country (model)
 *
 * Defines the data structure used to represent a single country.
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

/**
 * CountryList (collection / model)
 *
 * Defines a collection of Country's as well as the remote endpoint used
 * for synchronizing country data. Note that CountryList is a read-only
 * data structure on the client side.
 */
var CountryList = Backbone.Collection.extend({
    model: Country,
    // Single endpoint to manage all countries and hotness scores.
    url: '/api',
    initialize: function() {
        _.bindAll(this, 'parse');
    },
    parse: function(response) {
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
        this.model.each(function(country) {
            if (country.get('available')) {
                var hotness = country.get('hotness').current;
                // Paint the country based on what the current hotness value is.
                if (hotness > 1.0) country.get('element').classList.add('heatmap-3');
                else if (hotness > 0.65) country.get('element').classList.add('heatmap-2');
                else if (hotness > 0.25) country.get('element').classList.add('heatmap-1');
                else country.get('element').classList.add('heatmap-0');
            // If data isn't available, remove any classes that indicate that it
            // is available.
            } else {
                country.get('element').classList.remove('heatmap-0');
                country.get('element').classList.remove('heatmap-1');
                country.get('element').classList.remove('heatmap-2');
                country.get('element').classList.remove('heatmap-3');
            }
        });
    },
});

module.export = {
    Country: Country,
    CountryList: CountryList,

}