const todaynews = {
    template: `
    <div class="column content">
    <div class="newsbox">
    <transition-group v-bind:name="direction" tag="div" mode="out-in">
    	<news-item 
    	ref="curnews"
    	v-for="(item, index) in newslist"
    	v-bind:key="item.topic"
    	v-bind:news="item.news"
	v-bind:topic="item.topic"
    	v-bind:keywords="item.keywords"
    	v-bind:timeline="item.timelines.length"
    	v-bind:hotspot="item.hotspot.index"
    	v-bind:index="index"
    	v-on:hotspot_clk="handle_hotspot_clk"
    	v-on:timeline_clk="handle_timeline_clk"
    	v-on:news_detail="handle_news_detail"
    	class="slide-item"/>
    	<div
    	v-if="has_hotspot_graph"
    	key="hotspot_graph"
    	class="newsbox-item-graph">
    	<hotspot-graph 
    	v-bind:news_hotspot="hotspot.news"	
    	v-bind:words_hotspot="hotspot.words"/>
    	</div>
	<div
    	v-if="has_timeline_graph"
    	key="timeline_graph"
    	class="newsbox-item-graph">
    	<timeline-graph v-bind:timelines="timelines"/>
    	</div>
    </transition-group>
    </div>
    <div class="pageflip">
    	<dot-paging
    	ref="dot"
    	v-bind:pages="pagesnum"
    	v-bind:index="page"
    	v-on:change="page_change">
    	</dot-paging>
    </div>
    <news-modal 
    v-if="has_news_detail"
    v-on:close="handle_news_detail_close">
    <p slot="content">{{news_detail.content}}</p>
    </news-modal>
    </div>
    `,
    data : function() {
	return {
	    newsnum : 4,
	    pagesnum : 2,
	    page : 1,
	    size : 2,
	    direction : "slide-right",
	    has_hotspot_graph : false,
	    has_timeline_graph : false,
	    has_news_detail : false,
	    templist : [],
	    newslist: [],
	    timelines: {},
	    hotspot: {},
	    news_detail: {}
	}
    },
    methods : {
	get_newslist : function() {
	    let url = '/api/subtopics/today';
	    this.$http.get(url, {
		params: {page: this.page, size: this.size}
	    })
	    .then(({body}) => {
		console.log(body)
		this.newslist = body;
	    })
	},
	get_newslist_num : function() {
	    let url = '/api/subtopics/today/total';
	    this.$http.get(url)
	    .then(({body}) => {
		console.log(body)
		this.newsnum = Number(body);
		this.pagesnum = Math.ceil(this.newsnum/this.size);
	    })
	},
	page_change : function(page) {
	    last = this.page;
	    this.has_hotspot_graph = false;
	    this.has_timeline_graph = false;
	    if (last < page) {
		this.direction = "slide-right";
	    } else {
		this.direction = "slide-left";
	    }
	    this.page = page;
	    this.get_newslist();
	},
	handle_hotspot_clk : function(payload) {
	    index = payload.index;
	    clicked = payload.clicked;
	    if (clicked) {
		this.templist = this.newslist;
		this.newslist = [this.newslist[index],];
		this.hotspot = this.newslist[0].hotspot;
		this.has_hotspot_graph = true;
	    } else {
		this.has_hotspot_graph = false;
		this.newslist = this.templist;
	    }
	},
	handle_timeline_clk : function(payload) {
	    index = payload.index;
	    clicked = payload.clicked;
	    if (clicked) {
		this.templist = this.newslist;
		this.newslist = [this.newslist[index],];
		this.timelines = this.newslist[0].timelines;
		this.has_timeline_graph = true;
	    } else {
		this.has_timeline_graph = false;
		this.newslist = this.templist;
	    }
	},
	handle_news_detail : function(payload) {
	    this.news_detail = payload.news_item;
	    this.has_news_detail = true;
	},
	handle_news_detail_close : function() {
	    this.has_news_detail = false;
	}
    },
    created : function() {
	this.page = 1;
	this.size = 2;
	this.get_newslist_num();
	this.get_newslist();
    }
}

const news_item = {
    template: `
    <div class="newsbox-item">
	<h1 class="newsbox-title">{{ topic }}</h1>
	<div class="newsbox-keyword">
	    <h1 v-for="keyword in keywords">{{ keyword }}</h1>
	</div>
	<div class="newsbox-attr">
	    <a v-on:click="clk('hotspot')" 
    	    v-bind:class="{hover:is_hotspot_clk}">
		<h1>{{ hotspot }}</h1>
		<p>HotSpot</p>
	    </a>
	    <a v-on:click="clk('timeline')"
    	    v-bind:class="{hover:is_timeline_clk}">
		<h1>{{ timeline }}</h1>
		<p>Timeline</p>
	    </a>
	</div>
	<div class="newsbox-list">
	    <ul>
		<li v-for="item in news">
		    <a v-on:click="detail(item)">{{item.title}}</a>
		</li>
	    </ul>
	</div>
    </div>
    `,
    props: [
	'news',
	'keywords',
	'topic',
	'hotspot',
	'timeline',
	'index'
    ],
    data: function() {
	return {
	    is_hotspot_clk: false,
	    is_timeline_clk: false
	}
    },
    methods: {
	clk: function(from) {
	    if (from==='hotspot' && !this.is_timeline_clk) {
		this.is_hotspot_clk = !this.is_hotspot_clk;
		this.$emit('hotspot_clk', {
		    clicked : this.is_hotspot_clk,
		    index : this.index
		});
	    } else if (from==='timeline' && !this.is_hotspot_clk){
		this.is_timeline_clk = !this.is_timeline_clk;
		this.$emit('timeline_clk', {
		    clicked : this.is_timeline_clk,
		    index : this.index
		});
	    }
	},
	detail: function(item) {
	    console.log(item)
	    this.$emit('news_detail', {
		news_item : item
	    })
	}
    }

}

const dot_paging = {
    template: `
	<div class="dotstyle dotstyle-smalldotstroke">
    	<ul>
    	<li
    	v-for="page in pages"
    	v-bind:class="{current: page === index}"
	v-on:click="go(page)"
    	><a>{{page}}</a></li>
    	</ul>
    	</div>
    `,
    props : {
	pages : {
	    type : Number,
	    default : 5
	},
	index : {
	    type : Number,
	    default : 1
	}
    },
    methods : {
	go : function(page) {
	    this.$emit('change', page);
	}
    },
}

const news_graph_hotspot_upper = {
    extends : VueChartJs.Bar,
    props : ['hotspot_upper'],
    data : function() {
	return {
	    hotspot_dates: this.hotspot_upper.labels,
	    hotspot_data: this.hotspot_upper.data,
	    data_prop : {},
	    options: {
		responsive: true, 
		maintainAspectRatio: false,
		scales: {
		    xAxes: [{
			barPercentage: 0.5,
			gridLines : {
			    display: false,
			    drawBorder: false
			},
			ticks : {
			    fontSize: 8,
			    autoSkip: true,
			    autoSkipPadding: 5
			}
		    }],
		    yAxes: [{
			gridLines : {
			    display :false,
			    drawBorder: false
			},
			ticks : {
			    display: false
			}
		    }]
		},
		legend: {
		    display: false,
		},
		layout: {
		    padding: {
			left: 10,
		    }
		},
		title: {
		    display: true,
		    text: "热度指数"
		},
		
	    }
	}
    },
    created : function() {
	this.data_prop = {
	    labels: this.hotspot_dates,
	    datasets: [
	    {
	      label: 'Hotspot',
	      backgroundColor: '#333333',
	      hoverBackgroundColor: '#555555',
	      data: this.hotspot_data,
	      datalabels: {
		  display: false
	      }
	    },
	    ]
	}
    },
    mounted : function() {
	this.renderChart(this.data_prop, this.options);
    }
}

const news_graph_hotspot_lower = {
    extends : VueChartJs.Line,
    props: ['hotspot_lower'],
    data : function() {
	return {
	    hotspot_dates: this.hotspot_lower.labels,
	    hotspot_data: this.hotspot_lower.data,
	    colors : ['#A1B996','#E2814C','#32A198','#25A5F5','#042B35', '#C94C22'],
	    data_prop : {},
	    options: {
		responsive: true, 
		maintainAspectRatio: false,
		scales: {
		    xAxes: [{
			gridLines : {
			    display :false
			}
		    }],
		    yAxes: [{
			gridLines : {
			    display :false
			}
		    }]
		},
		elements: {
		    line: {
			tension: 0 // disables bezier curves
		    },
		    point: {
			radius: 2.5,  //point radius
			backgroundColor: '#222222',
			hoverRadius: 5
		    }
		},
		legend: {
		    display: true,
		    fullWidth: false,
		    position: 'right',
		    labels : {
			boxWidth : 15,
			fontSize : 10
		    }
		},
		layout: {
		    padding: {
			left: 10,
			top: 15
		    }
		},
		plugins: {
		    datalabels: {
			backgroundColor: '#333333',
			borderRadius: 4,
			color: 'white',
			font: {
			    weight: 'bold'
			},
			formatter: Math.round
		    }
		}
	    }
	}
    },
    created : function() {
	var sets = [];
	const colors = this.colors;
	this.hotspot_data.forEach(function(item,index)
	{
	    console.log(item, index);
	    var set = {
		label: item[0],
		borderColor: colors[index],
		data: item[1],
		fill: false,
		datalabels: {
		  anchor: 'end',
		  align: 'center'
		}
	    }
	    sets.push(set);
	})
	this.data_prop = {
	    labels: this.hotspot_dates,
	    datasets: sets
	}
    },
    mounted : function() {
	this.renderChart(this.data_prop, this.options);
    }
}

const hotspot = {
    template: `
    <div class="column content">
    <wordcloud
    canvas_id="cloud-hotspot"/>
    <div class="newslist">
	<ul>
	    <li v-for="item in subtopics">
		<a>{{item.title}}</a>
	    </li>
	</ul>
    </div>
    </div>
    `,
    data : function() {
	return {
	    subtopics : []
	}
    },
    methods : {
	get_subtopics : function() {
	    let url = '/api/hotspots/subtopics/today';
	    this.$http.get(url)
	    .then(({body}) => {
		console.log(body);
		this.subtopics = body;
	    })
	},
    },
    created : function() {
	this.get_subtopics();
    },
    mounted : function() {
    }
}

const wordcloud = {
    template: `
    <div 
    class="wordcloud"
    v-bind:id="canvas_id">
    </div>
    `,
    data : function() {
	return {
	    c_id : this.canvas_id,
	    data_options : this.options,
	    list : [],
	    map : {}
	}
    },
    props : {
	canvas_id : {
	    type: String,
	    default: "wordcloud-hotspot"
	},
	options : {
	    type: Object,
	    default :function() {
		return {
		    gridSize : 52,
		    minSize : 10,
		    weightFactor : function (size) {
			return Math.pow(size, 0.5) * 4
		    },
		    rotateRatio: 0.01,
		    rotationSteps: 2,
		    shuffle: true,
		    color: function(word, weight) {
			color = '';
			if (weight >= 150) {
			    color = '#222222';
			} else if (weight >= 100) {
			    color = '#444444';
			} else if (weight >= 35) {
			    color = '#555555';
			} else {
			    color = '#666666';
			}
			return color;
		    },
		}
	    }
	},
    },
    methods : {
	gen_wordcloud : function() {
	    var canvas = document.getElementById(this.c_id);
	    console.log(canvas.id + " Hello");
	    let url = '/api/hotspots/words/today';
	    this.$http.get(url)
	    .then(({body}) => {
		console.log(body);
		this.data_options.list = body.list;
		this.map = body.news;
		WordCloud(canvas, this.data_options);
	    })
	},
	gen_tooltips : function() {
	    var canvas = document.getElementById(this.c_id);
	    for (let i = 0;i < canvas.childElementCount;i++) {
		var span = canvas.children[i];
		var tooltip = document.createElement('span');
		tooltip.className = "tooltip";
		tooltip.innerText = this.map[span.innerText].join(' |\n');
		span.appendChild(tooltip);
	    }
	}
    },
    mounted : function() {
	this.gen_wordcloud();
	setTimeout(this.gen_tooltips, 3000);
    }
}

const timeline_graph = {
    template : `
    <ul class="timeline">
	<li v-for="(item, index) in timelines"
	class="clearfix timeline-item">
	    <div class="timeline-item-left">
		<h1 v-if="index % 2 == 0">{{ item.date }}</h1>
		<span v-if="index % 2 != 0" 
    		class="timeline-line"></span>
		<h1 v-if="index % 2 != 0" 
    		class="timeline-title">
    		{{ item.title }}
		    <div class="tooltip"><p>{{ item.extraction }}</p></div>
    		</h1>
	    </div>
	    <div class="timeline-item-circle"><a></a></div>
	    <div class="timeline-item-right">
		<span v-if="index % 2 == 0" 
    		class="timeline-line"></span>
		<h1 v-if="index % 2 == 0" 
    		class="timeline-title">{{ item.title }}<div class="tooltip"><p>{{ item.extraction }}</p></div></h1>
		<h1 v-if="index % 2 != 0">{{ item.date }}</h1>
	    </div>
	</li>
    </ul>
    `,
    props: ['timelines']
}

const hotspot_graph = {
    template: `
    <div>
    <news-graph-hotspot-upper
    v-bind:hotspot_upper="news_hotspot"
    class="upper"/>
    <news-graph-hotspot-lower
    v-bind:hotspot_lower="words_hotspot"
    class="lower"/>
    </div>
    `,
    props: [
	'news_hotspot',
	'words_hotspot'
    ]
}

const news_modal = {
    template:`
    <transition name="modal">
    <div class="modal-mask">
    <div class="modal-wrapper">
    <div class="modal-container">
    <slot name="content"></slot>
    <button 
    class="modal-close-button"
    v-on:click="$emit('close')">OK</button>
    </div>
    </div>
    </div>
    </transition>
    `
}

const topic_search = {
    template: `
    <div class="column content">
    <searchbox
    v-on:searched="get_search_res">
    </searchbox>
    <div 
    class="clearfix search-response"
    v-if="is_searched" 
    v-bind:class="{visible: is_searched}">
    	<div class="item-center">
	<news-item 
    	v-if="has_newsbox"
    	ref="resnews"
    	v-bind:key="item.topic"
    	v-bind:news="item.news"
	v-bind:topic="item.topic"
    	v-bind:keywords="item.keywords"
    	v-bind:timeline="item.timelines.length"
    	v-bind:hotspot="item.hotspot.index"
    	v-on:hotspot_clk="handle_hotspot_clk"
    	v-on:timeline_clk="handle_timeline_clk"
    	v-bind:class="{'newsbox-item-withgraph': has_hotspot_graph||has_timeline_graph}">
    	</news-item>
    	<h1 class="noresult"
    	v-if="has_newsbox === false">{{message}}</h1>
	<div
    	key="graph_search"
    	class="newsbox-item-graph"
    	v-bind:class="{'newsbox-item-graph-visible': has_hotspot_graph||has_timeline_graph}">
	<transition name="slide-up" tag="div">
    	<hotspot-graph 
    	v-if="has_hotspot_graph"
    	v-bind:news_hotspot="item.hotspot.news"	
    	v-bind:words_hotspot="item.hotspot.words"/>
    	<timeline-graph 
    	v-if="has_timeline_graph"
    	v-bind:timelines="item.timelines"/>
    	</transition>
    	</div>
    	</div>
	<div class="pageflip-vertical">
	    <dot-paging
	    ref="dot-vertical"
	    v-bind:pages="newslist.length"
	    v-bind:index="page"
	    v-on:change="page_change">
	    </dot-paging>
	</div>
    </div>
    </div>
    `,
    data: function() {
	return {
	    is_searched: false,
	    has_hotspot_graph: false,
	    has_timeline_graph: false,
	    has_newsbox: false,
	    message: 'Please wait',
	    search_words: '',
	    newslist: [],
	    item: {},
	    page: 1
	}
    },
    methods: {
	page_change(page) {
	    this.page = page;
	    this.has_hotspot_graph = false;
	    this.has_timeline_graph = false;
	    this.item = this.newslist[page - 1];
	},
	handle_hotspot_clk : function(payload) {
	    index = payload.index;
	    clicked = payload.clicked;
	    if (clicked) {
		this.has_hotspot_graph = true;
	    } else {
		this.has_hotspot_graph = false;
	    }
	},
	handle_timeline_clk : function(payload) {
	    index = payload.index;
	    clicked = payload.clicked;
	    if (clicked) {
		this.has_timeline_graph = true;
	    } else {
		this.has_timeline_graph = false;
	    }
	},
	get_search_res: function(words) {
	    this.is_searched = true;
	    console.log("Searching ", words);
	    let url = '/api/search/' + words;
	    this.$http.get(url)
	    .then(({body}) => {
		console.log(body);
		this.page = 1
		this.newslist = body
		if (this.newslist.length > 0) {
		    this.has_newsbox = true;
		    this.item = this.newslist[this.page - 1];
		} else {
		    this.message = 'Sorry. No results'
		    this.has_newsbox = false;
		}
	    })
	},
    }
}

const search_box = {
    template: `
    <div class="searchbox"
    v-bind:class="{searched: is_searched}">
    	<div class="clearfix search-icon">
	    <topicsearch-icon></topicsearch-icon>
	    <h1>话题搜索</h1>
    	</div>
    	<div class="inputbox">
    	<input 
    	v-model.trim="search_words" 
    	type="text" 
    	name="search-content">
	<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xl="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="439.38653 116.85633 38 24" width="38" height="24"
    	v-on:click="search">
	    <g id=“enter-icon” fill-opacity="1" stroke-dasharray="none" stroke="none" stroke-opacity="1" fill="none">
		<path d="M 473.38653 118.85633 L 473.38653 126.85633 L 447.04653 126.85633 L 454.20653 119.67633 L 451.38653 116.85633 L 439.38653 128.85633 L 451.38653 140.85633 L 454.20653 138.03633 L 447.04653 130.85633 L 477.38653 130.85633 L 477.38653 118.85633 Z" fill="black"/>
	    </g>
	</svg>
    	</div>
    </div>
    `,
    data: function() {
	return {
	    search_words: '',
	    is_searched: false
	}
    },
    methods : {
	search: function() {
	    console.log(this.search_words);
	    this.is_searched = true;
	    this.$emit("searched", this.search_words);
	}
    }
}

const timeline = {
    template: `
    <div v-if="visible" class="column content">
    	<div class="content-timeline">
    		<div class="topic-timeline">
    		<h1>{{timeline_item.topic}}</h1>
    		</div>
		<div class="clearfix info-timeline">
    		<div class="keywords-timeline">
		    <h1 v-for="keyword in timeline_item.keywords">
    			{{keyword}}
    		    </h1>
    		</div>
    		<div class="graph-timeline">
		    <timeline-graph 
		    v-bind:timelines="timeline_item.timelines"/>
    		</div>
    		</div>
    	</div>
    	<div class="paging-timeline">
	    <dot-paging
		ref="dot-vertical-timeline"
		v-bind:pages="pages"
		v-bind:index="page"
		v-on:change="page_change">
	    </dot-paging>
    	</div>
    	<div class="datechunk-timeline">
	<ul>
	<li 
	    v-bind:class="{hover: day_range == 7}"
	    v-on:click="day_range_change(7)">
	    近一周新闻时间线
    	</li>
	<li 
	    v-bind:class="{hover: day_range == 14}"
	    v-on:click="day_range_change(14)">
	    近两周新闻时间线
	</li>
	<li 
	    v-bind:class="{hover: day_range == 30}"
	    v-on:click="day_range_change(30)">
	    近一月新闻时间线
    	</li>
    	</ul>
    	</div>
    </div>
    `,
    data: function() {
	return {
	    page: 1,
	    pages: 5,
	    day_range: 14,
	    timeline_item: {},
	    timeline_res: [],
	    visible: false,
	}
    },
    methods: {
	day_range_change(day_range) {
	    this.day_range = day_range;
	    let url = '/api/timelines/days/' + this.day_range;
	    this.$http.get(url)
	    .then(({body}) => {
		console.log(body);
		this.page = 1
		this.timeline_res = body;
		this.timeline_item = this.timeline_res[this.page - 1];
		this.pages = this.timeline_res.length;
	    })
	},
	page_change(page) {
	    this.page = page;
	    this.timeline_item = this.timeline_res[page - 1]
	},
	get_timeline_res: function() {
	    let url = '/api/timelines/days/' + this.day_range;
	    this.$http.get(url)
	    .then(({body}) => {
		console.log(body);
		this.visible = true;
		this.timeline_res = body;
		this.timeline_item = this.timeline_res[this.page - 1]
		this.pages = this.timeline_res.length
	    })
	},
    },
    created: function() {
	this.get_timeline_res();
    },
    mounted: function() {
    }
}

Vue.component('news-item', news_item);
Vue.component('dot-paging', dot_paging);
Vue.component('news-graph-hotspot-upper', news_graph_hotspot_upper);
Vue.component('news-graph-hotspot-lower', news_graph_hotspot_lower);
Vue.component('wordcloud', wordcloud);
Vue.component('timeline-graph', timeline_graph);
Vue.component('hotspot-graph', hotspot_graph);
Vue.component('searchbox', search_box);
Vue.component('news-modal', news_modal);

var router = new VueRouter({
    routes: [
	{path: '/todaynews', component: todaynews},
	{path: '/hotspot', component: hotspot},
	{path: '/topicsearch', component: topic_search},
	{path: '/timeline', component: timeline}
    ]
})

var app = new Vue({
    router
}).$mount('#app')

router.push('/todaynews');

