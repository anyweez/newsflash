var express = require('express');
var router = express.Router();

/* GET JSON response from backend. */

router.get('/', function(req, res, next) {
    res.json({ 
        countries: [{
            id: 'US',
            // Hotness scores that are displayed in the frontend.
            hotness: {
                current: .91,   // Absolute, [0, 1]
                last7: .3,      // Relative, now vs seven days ago (30% higher here)
                last30: .12,    // Relative, now vs thirty days ago (12% higher here)
            },
            // Name of the current leader, for display.
            current_leader: "Barack Obama",
            // List of stories to display, pre-ranked.
            stories: [{
                title: "Serverside story",
                url: "https://www.story1.com",
            }],
            // ID's for "related" countries, i.e. countries that are appearing in the
            // news with this country now.
            related_countries: [{
                id: "RU",
                hotness: {
                    current: .91,
                    last7: .3,
                    last30: .12,
                },
            }, {
               id: "IR",
                hotness: {
                    current: .91,
                    last7: .3,
                    last30: .12,
                },
            }, {
                id: "JP",
                hotness: {
                    current: .91,
                    last7: .3,
                    last30: .12,   
                }
            }],
        }],
    });
});

module.exports = router;