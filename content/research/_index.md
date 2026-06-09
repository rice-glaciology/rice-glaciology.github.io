---
title: Research
date: 2025-04-10
type: landing

sections:
  - block: markdown
    content:
      title: ""
      text: |
        <div class="research-carousel">

          <div class="research-slide active">
            <h2 class="research-slide-title">Ice Flow</h2>
            <p class="research-slide-body">Englacial stresses cause ice to creep internally, with rates that depend strongly on temperature and on the evolving microstructure of crystal grains. In my group, we model glacier and ice-sheet motion to understand how englacial viscosity of the ice sheet and assumptions about slip at the ice-base interface affect glacier retreat. Using the finite element method and models like elmer/ice and icepack, we can solve equations that describe glacier flow and use some of the unique data our group collects to constrain physical processes that contribute to motion.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Multi-Element Radar</h2>
            <p class="research-slide-body">In my group, we also develop and use multi-element radar systems to image the internal structure, englacial properties, and basal conditions of glaciers and ice sheets. These systems can be used to geolocate off-nadir energy and construct 3D images of the ice-base topography and the 3D englacial structure of the ice sheet. Repeating these surveys, we can also perform multipass processing, which combines repeat surveys, coregisters passes, and performs coherent processing before interfering the coregistered profiles to map vertical displacement, strain rates, and vertical velocity. These data provide distributed observations of englacial deformation that are under-used in ice-flow model initialization.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Firn</h2>
            <p class="research-slide-body">Firn is the porous snow layer that compacts into glacier ice. Firn density, temperature, and energy evolution shape surface elevation change and set the radar wave speed, which feeds directly into satellite altimetry and radar-estimates of englacial structure. Our group has built firn models in a finite-element framework so compaction, heat transport, and meltwater processes can be solved consistently and used with inverse methods to assimilate observations of compaction to initialize poorly constrained densification parameters. These constraints improve the interpretation of radar travel times, satellite altimetry trends, and can be used to reconstruct past climate from firn observations.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Submarine Ice-Shelf Melt</h2>
            <p class="research-slide-body">Warm salty ocean water can circulate beneath ice shelves and melt them from below. Ice shelves float, so this melt does not raise sea level directly, but thinning reduces buttressing and can speed up the flow of grounded ice into the ocean. The IPCC links much of West Antarctica's observed mass loss since the early 1990s to changes in ice shelves driven by basal melting, and estimates of Antarctic basal meltwater flux are on the order of 1100 to 1600 gigatons per year in recent decades. Antarctica's grounded ice loss has already raised global mean sea level by about 7.4 ± 1.5 mm since 1992. Our group is developing methods that use time series of high-resolution stereo satellite imagery to map elevation change over floating ice. Repeated stereo DEMs are co-registered and differenced, then combined with estimates of englacial stresses and surface mass balance to isolate basal melt rates.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Sea-Level Geophysics</h2>
            <p class="research-slide-body">Along the Gulf Coast, relative sea level change is also affected by subsidence connected to fluid extraction and glacial isostatic adjustment. As part of local fieldwork, we combine multi-mission InSAR and GNSS observations to map contemporary land motion at neighborhood scales, and use Bayesian poromechanical models to project subsidence under scenarios of recharge, pumping, and extraction. These modeling and remote observations complement a growing network of GNSS interferometric reflectometry tide-gauge stations our group is maintaining in southeastern Texas. Together, these data and models can be used to represent regional processes contributing to vertical land motion (VLM) in probabilistic frameworks like FACTS. Our group also works closely with CFAR and SPEED to incorporate our observations and simulations in community vulnerability metrics that inform planning.</p>
          </div>

          <div class="research-carousel-nav">
            <button class="research-prev" aria-label="Previous">&#8592;</button>
            <div class="research-dots"></div>
            <button class="research-next" aria-label="Next">&#8594;</button>
          </div>

        </div>

        <script>
        (function() {
          var slides = document.querySelectorAll('.research-slide');
          var dotsContainer = document.querySelector('.research-dots');
          var current = 0;

          slides.forEach(function(_, i) {
            var dot = document.createElement('button');
            dot.className = 'research-dot' + (i === 0 ? ' active' : '');
            dot.setAttribute('aria-label', 'Slide ' + (i + 1));
            dot.addEventListener('click', function() { goTo(i); });
            dotsContainer.appendChild(dot);
          });

          function goTo(n) {
            slides[current].classList.remove('active');
            document.querySelectorAll('.research-dot')[current].classList.remove('active');
            current = (n + slides.length) % slides.length;
            slides[current].classList.add('active');
            document.querySelectorAll('.research-dot')[current].classList.add('active');
          }

          document.querySelector('.research-prev').addEventListener('click', function() { goTo(current - 1); });
          document.querySelector('.research-next').addEventListener('click', function() { goTo(current + 1); });
        })();
        </script>

    design:
      columns: '1'
---
