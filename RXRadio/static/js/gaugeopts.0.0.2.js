//refresh dev file

//SHT Project
//Gauge Options
//Marcus Dechant (c)
//v0.0.2

var optsTemp = {
    angle: -0, 
    lineWidth: 0.4, 
    radiusScale: 0.95, 
    pointer: {
        length: 0.6, 
        strokeWidth: 0.035, 
        color: '#434343' 
    },
    limitMax: false,     
    limitMin: false,     
    staticZones: [
        {strokeStyle: "#C80000", min: 0, max: 12.4},
        {strokeStyle: "#FF8200", min: 12.5, max: 18.9},
        {strokeStyle: "#008000", min: 19, max: 25.9 },
        {strokeStyle: "#FF8200", min: 26, max: 32.5},
        {strokeStyle: "#C80000", min: 32.6, max: 45},
    ],
    strokeColor: '#000000',
    highDpiSupport: true, 
    staticLabels: {
        font: "10px sans-serif",
        labels: [0, 5, 10, 15, 20, 25, 30, 35, 40, 45],
        color: "#000000",
    },
};
var optsHumi = {
    angle: -0, 
    angle: -0, 
    lineWidth: 0.4, 
    radiusScale: 0.95, 
    pointer: {
        length: 0.6, 
        strokeWidth: 0.035,
        color: '#434343'
    },
    limitMax: false,
    limitMin: false,
    staticZones: [
        {strokeStyle: "#C80000", min: 0, max: 14.9},
        {strokeStyle: "#FF8200", min:15 , max: 29.9},
        {strokeStyle: "#008000", min: 30, max: 84.9},
        {strokeStyle: "#FF8200", min: 85, max: 100},
    ],
    strokeColor: '#000000',
    highDpiSupport: true,
    staticLabels: {
        font: "10px sans-serif",
        labels: [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100],
        color: "#000000",
    },
};