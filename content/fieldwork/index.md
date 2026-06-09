---
title: Fieldwork
date: 2025-04-10
type: landing

sections:
  - block: markdown
    id: fieldwork
    content:
      title: Fieldwork
      text: |
        <style>
        .fw-app{font-family:'Inter',sans-serif;display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-start;justify-content:center}
        .fw-gcol{flex:1 1 360px;min-width:280px;max-width:480px}
        .fw-gcol svg{width:100%;height:auto;display:block;cursor:grab;touch-action:none}
        .fw-gcol svg:active{cursor:grabbing}
        .fw-hint{font-size:.8rem;color:#999;text-align:center;margin:.6rem 0 0;font-weight:300}
        .fw-side{flex:1 1 240px;min-width:220px}
        .fw-card{background:#f7f7f5;padding:1.1rem 1.25rem}
        .fw-region{font-size:.72rem;color:#4a9aab;letter-spacing:.1em;text-transform:uppercase;margin:0 0 .35rem}
        .fw-title{font-size:1.15rem;font-weight:400;margin:0 0 .5rem;color:#111}
        .fw-text{font-size:.95rem;line-height:1.65;color:#333;font-weight:300;margin:0}
        </style>

        <div class="fw-app">
          <div class="fw-gcol"><div id="fw-holder"></div><p class="fw-hint">Drag to spin &middot; click a marker to learn more</p></div>
          <aside class="fw-side">
            <div class="fw-card">
              <p class="fw-region" id="fw-region">Field sites</p>
              <p class="fw-title" id="fw-title">Where we work</p>
              <p class="fw-text" id="fw-text">Our field campaigns span the Antarctic and Greenland ice sheets, the North Cascades, and the Texas Gulf Coast. Click a marker to read more.</p>
              <img id="fw-img" alt="" style="display:none;width:100%;margin-top:.9rem">
            </div>
          </aside>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
        <script>
        (function(){
          // ---- EDIT YOUR FIELD SITES HERE ----
          // Coordinates are approximate — adjust lat/lon as needed.
          // To add a photo: drop the image in content/fieldwork/ and add  img:"filename.jpg"  to that site.
          var SITES=[
            {name:"Thwaites Glacier",region:"West Antarctica",lat:-75.5,lon:-106.75,img:"",text:"Phase-sensitive radar (ApRES) and polarimetric surveys of basal conditions and englacial deformation on one of Antarctica's most rapidly changing glaciers."},
            {name:"Kamb Ice Stream",region:"Siple Coast, Antarctica",lat:-82.4,lon:-140.0,text:"Polarimetric radar studies of ice fabric and basal properties on a stagnated West Antarctic ice stream."},
            {name:"Beardmore Glacier",region:"Transantarctic Mountains",lat:-83.5,lon:171.0,text:"ApRES and radar surveys of a major outlet glacier draining the East Antarctic Ice Sheet."},
            {name:"Flask Glacier",region:"Antarctic Peninsula",lat:-65.8,lon:-62.3,text:"Radar and field studies of a tributary glacier in the former Larsen B embayment, where ice-shelf collapse reshaped glacier flow."},
            {name:"Hercules Dome",region:"West Antarctica",lat:-86.5,lon:-105.0,text:"Geophysical and radar surveys at a high-elevation ice dome — a candidate site for a deep ice core recording past ice-sheet and climate history."},
            {name:"South Pole",region:"East Antarctic Plateau",lat:-89.99,lon:0.0,text:"Firn, radar, and altimetry studies on the polar plateau near Amundsen–Scott South Pole Station."},
            {name:"Rothera",region:"Antarctic Peninsula",lat:-67.57,lon:-68.13,text:"Logistics hub for radar and geophysical campaigns on the Antarctic Peninsula."},
            {name:"EastGRIP",region:"Northeast Greenland",lat:75.63,lon:-35.99,text:"Polarimetric radar and firn studies at the East Greenland Ice-core Project on the Northeast Greenland Ice Stream."},
            {name:"Eqip Sermia",region:"West Greenland",lat:69.77,lon:-50.22,text:"Field studies of a fast-flowing tidewater outlet glacier in West Greenland."},
            {name:"Texas Gulf Coast",region:"Houston, Texas",lat:29.4,lon:-94.9,text:"GNSS and InSAR networks measuring vertical land motion and relative sea-level change along the Gulf Coast."},
            {name:"North Cascades",region:"Washington, USA",lat:48.7,lon:-121.2,text:"Glacier and seasonal-snow studies in the North Cascades of Washington State."}
          ];
          // -----------------------------------------------------------------
          var W=460,H=460,R=212;
          function start(){
            if(typeof d3==="undefined"||typeof topojson==="undefined"){return setTimeout(start,150);}
            var svg=d3.select("#fw-holder").append("svg").attr("viewBox","0 0 "+W+" "+H).attr("width","100%").attr("role","img").attr("aria-label","Interactive globe of our field sites");
            var proj=d3.geoOrthographic().scale(R).translate([W/2,H/2]).clipAngle(90).rotate([0,60]);
            var path=d3.geoPath(proj), grat=d3.geoGraticule10();
            svg.append("circle").attr("cx",W/2).attr("cy",H/2).attr("r",R).attr("fill","#eef1f3").attr("stroke","#dfe3e6");
            var gG=svg.append("path").attr("fill","none").attr("stroke","#e2e6e9").attr("stroke-width",.4);
            var gL=svg.append("path").attr("fill","#d7d4cc");
            var gM=svg.append("g");
            var auto;
            d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json").then(function(w){
              gL.datum(topojson.feature(w,w.objects.land));
              SITES.forEach(function(s,i){
                var g=gM.append("g");
                g.append("circle").attr("r",11).attr("fill","transparent").style("cursor","pointer")
                  .on("click",function(e){e.stopPropagation();select(i,true);}).append("title").text(s.name);
                g.append("circle").attr("class","mk").attr("r",4.5).attr("fill","#4a9aab").attr("stroke","#fff").attr("stroke-width",1.3).style("pointer-events","none");
                s._g=g;
              });
              redraw(); start_auto();
            }).catch(function(){d3.select("#fw-text").text("Couldn't load the map data — check the connection and reload.");});

            function redraw(){
              gG.attr("d",path(grat)); gL.attr("d",path);
              var c=proj.invert([W/2,H/2]);
              SITES.forEach(function(s){
                var vis=d3.geoDistance([s.lon,s.lat],c)<Math.PI/2-0.02, p=proj([s.lon,s.lat]);
                s._g.style("display",vis?null:"none");
                if(vis&&p)s._g.attr("transform","translate("+p[0]+","+p[1]+")");
              });
            }
            function select(i,fly){
              var s=SITES[i];
              d3.select("#fw-region").text(s.region); d3.select("#fw-title").text(s.name); d3.select("#fw-text").text(s.text);
              var im=d3.select("#fw-img"); if(s.img){im.attr("src",s.img).attr("alt",s.name).style("display","block");}else{im.style("display","none");}
              SITES.forEach(function(t,idx){t._g.select(".mk").attr("r",idx===i?6.5:4.5).attr("fill",idx===i?"#357989":"#4a9aab");});
              stop_auto();
              if(fly){var cur=proj.rotate(),ip=d3.interpolate(cur,[-s.lon,-s.lat]);d3.transition().duration(800).tween("r",function(){return function(t){proj.rotate(ip(t));redraw();};});}
            }
            function start_auto(){auto=d3.timer(function(){var r=proj.rotate();proj.rotate([r[0]+0.12,r[1]]);redraw();});}
            function stop_auto(){if(auto){auto.stop();auto=null;}}
            svg.call(d3.drag().clickDistance(8).on("start",stop_auto).on("drag",function(e){
              var r=proj.rotate(),k=0.4,ny=Math.max(-90,Math.min(90,r[1]-e.dy*k));
              proj.rotate([r[0]+e.dx*k,ny]);redraw();
            }));
          }
          start();
        })();
        </script>
    design:
      columns: '1'
---
