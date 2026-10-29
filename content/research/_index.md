---
title: Research
date: 2025-04-10
type: landing

sections:
  - block: markdown
    id: research
    content:
      title: Research
      text: |
        <div class="research-carousel">

          <div class="research-slide active">
            <h2 class="research-slide-title">Ice Flow</h2>
            <figure class="research-movie">
              <video muted loop playsinline preload="none" poster="/media/research/ice-flow.jpg" aria-label="Flowline model of two glaciers retreating after ocean melt removes their ice shelf">
                <source src="/media/research/ice-flow.mp4" type="video/mp4">
              </video>
              <figcaption>Model experiment: one marine glacier, one ocean forcing, two sliding laws. Both start from the same state; with Coulomb-limited sliding the grounding line crosses the ridge two centuries earlier.</figcaption>
            </figure>
            <p class="research-slide-body">Englacial stresses cause ice to creep internally, with rates that depend strongly on temperature and on the evolving microstructure of crystal grains. We model glacier and ice-sheet motion to understand how the englacial viscosity of the ice sheet and assumptions about slip at the ice-base interface affect glacier retreat. Using the finite element method and models like Elmer/Ice and icepack, we solve equations that describe glacier flow and use some of the unique data our group collects to constrain the physical processes that contribute to motion.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Multi-Element Radar</h2>
            <figure class="research-movie">
              <video muted loop playsinline preload="none" poster="/media/research/multi-element-radar.jpg" aria-label="Synthetic radar survey building a swath bed map, an echogram and vertical velocity profiles">
                <source src="/media/research/multi-element-radar.mp4" type="video/mp4">
              </video>
              <figcaption>Synthetic survey: the array maps a swath of bed instead of a single line, and repeat passes give vertical velocity through the ice column.</figcaption>
            </figure>
            <p class="research-slide-body">We develop and use multi-element radar systems to image the internal structure, englacial properties, and basal conditions of glaciers and ice sheets. These systems can geolocate off-nadir energy and construct 3D images of the ice-base topography and the englacial structure of the ice sheet. Repeating these surveys, we perform multipass processing &mdash; combining repeat surveys, coregistering passes, and interfering the coregistered profiles to map vertical displacement, strain rates, and vertical velocity. These data provide distributed observations of englacial deformation that are under-used in ice-flow model initialization.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Firn</h2>
            <figure class="research-movie">
              <video muted loop playsinline preload="none" poster="/media/research/firn.jpg" aria-label="Firn column densifying as climate warms, with density profile and firn air content change">
                <source src="/media/research/firn.mp4" type="video/mp4">
              </video>
              <figcaption>Model experiment: a Herron&ndash;Langway firn column under 4&nbsp;K of warming and 20&nbsp;% more snowfall, and the firn air it loses.</figcaption>
            </figure>
            <p class="research-slide-body">Firn is the porous snow layer that compacts into glacier ice. Firn density, temperature, and energy evolution shape surface elevation change and set the radar wave speed, which feeds directly into satellite altimetry and radar estimates of englacial structure. Our group builds firn models in a finite-element framework so that compaction, heat transport, and meltwater processes can be solved consistently and used with inverse methods to assimilate observations of compaction and initialize poorly constrained densification parameters. These constraints improve the interpretation of radar travel times and satellite altimetry trends, and can be used to reconstruct past climate from firn observations.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Submarine Ice-Shelf Melt</h2>
            <figure class="research-movie">
              <video muted loop playsinline preload="none" poster="/media/research/submarine-melt.jpg" aria-label="Ice shelf with a melt channel, stereo DEM strips arriving, and a melt map filling in">
                <source src="/media/research/submarine-melt.mp4" type="video/mp4">
              </video>
              <figcaption>Synthetic example: repeat stereo DEMs track ice through a basal channel; elevation change along flow gives the melt rate where strips overlap.</figcaption>
            </figure>
            <p class="research-slide-body">Warm, salty ocean water can circulate beneath ice shelves and melt them from below. Ice shelves float, so this melt does not raise sea level directly, but thinning reduces buttressing and can speed up the flow of grounded ice into the ocean. Our group develops methods that use time series of high-resolution stereo satellite imagery to map elevation change over floating ice. Repeated stereo DEMs are co-registered and differenced, then combined with estimates of englacial stresses and surface mass balance to isolate basal melt rates.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Sea-Level Geophysics</h2>
            <figure class="research-movie">
              <video muted loop playsinline preload="none" poster="/media/research/sea-level-geophysics.jpg" aria-label="Subsidence map from InSAR and GNSS with projections of land motion and relative sea level">
                <source src="/media/research/sea-level-geophysics.mp4" type="video/mp4">
              </video>
              <figcaption>Synthetic example on an invented coastline: InSAR and GNSS observe subsidence, and a compaction model projects it under two pumping scenarios.</figcaption>
            </figure>
            <p class="research-slide-body">Along the Gulf Coast, relative sea-level change is also affected by subsidence connected to fluid extraction and glacial isostatic adjustment. Through local fieldwork, we combine multi-mission InSAR and GNSS observations to map contemporary land motion at neighborhood scales, and use Bayesian poromechanical models to project subsidence under scenarios of recharge, pumping, and extraction. These observations complement a growing network of GNSS interferometric reflectometry tide-gauge stations our group maintains in southeastern Texas. Together, these data and models represent regional processes contributing to vertical land motion in probabilistic frameworks like FACTS, and we work closely with community partners to inform planning.</p>
          </div>

          <div class="research-carousel-nav">
            <button class="research-prev" aria-label="Previous">&#8592;</button>
            <div class="research-dots"></div>
            <button class="research-next" aria-label="Next">&#8594;</button>
          </div>

        </div>

        <script>
        (function() {
          var slides = document.querySelectorAll('#research .research-slide');
          var dotsContainer = document.querySelector('#research .research-dots');
          if (!slides.length || !dotsContainer) return;
          var current = 0;

          slides.forEach(function(_, i) {
            var dot = document.createElement('button');
            dot.className = 'research-dot' + (i === 0 ? ' active' : '');
            dot.setAttribute('aria-label', 'Slide ' + (i + 1));
            dot.addEventListener('click', function() { goTo(i); });
            dotsContainer.appendChild(dot);
          });

          // Movies: play only the visible slide's, and only while the carousel is on screen.
          // With reduced motion, show the poster and controls instead of autoplaying.
          var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          var onScreen = true;
          function syncVideos() {
            slides.forEach(function(slide, i) {
              var v = slide.querySelector('video');
              if (!v) return;
              if (reduce) { v.controls = true; return; }
              if (i === current && onScreen) {
                if (v.preload !== 'auto') { v.preload = 'auto'; }
                var p = v.play();
                if (p && p.catch) p.catch(function() { v.controls = true; });
              } else {
                v.pause();
              }
            });
          }
          if ('IntersectionObserver' in window) {
            new IntersectionObserver(function(entries) {
              onScreen = entries[0].isIntersecting;
              syncVideos();
            }, { threshold: 0.25 }).observe(document.querySelector('#research .research-carousel'));
          }

          function goTo(n) {
            slides[current].classList.remove('active');
            document.querySelectorAll('#research .research-dot')[current].classList.remove('active');
            current = (n + slides.length) % slides.length;
            slides[current].classList.add('active');
            document.querySelectorAll('#research .research-dot')[current].classList.add('active');
            syncVideos();
          }

          document.querySelector('#research .research-prev').addEventListener('click', function() { goTo(current - 1); });
          document.querySelector('#research .research-next').addEventListener('click', function() { goTo(current + 1); });
          syncVideos();
        })();
        </script>
    design:
      columns: '1'
---
