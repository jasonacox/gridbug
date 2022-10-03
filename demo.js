{
	"nodes": [{
			"data": {
				"id": "localhost"
			}
		},
		{
			"data": {
				"id": "jasonacox"
			}
		},
		{
			"data": {
				"id": "thread"
			}
		}
	],
	"edges": [{
			"data": {
				"id": "localhost.jasonacox",
				"source": "localhost",
				"target": "jasonacox",
				"color": "red"
			}
		},
		{
			"data": {
				"id": "jasonacox.localhost",
				"source": "jasonacox",
				"target": "localhost",
				"color": "green"
			}
		},
		{
			"data": {
				"is": "jasonacox.thread",
				"source": "jasonacox",
				"target": "thread",
				"color": "blue"
			}
		}
	]
}