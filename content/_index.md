---
title:
date: 2025-04-10
type: landing

sections:
  # ===== ABOUT =====
  - block: markdown
    id: about
    content:
      title: About Us
      text: |
        <div class="about-bio">
          <p>We are the <strong>Rice Glaciology</strong> group in the Department of Earth, Environmental and Planetary Sciences at <a href="https://earthscience.rice.edu/" target="_blank" rel="noopener">Rice University</a>. We study how ice sheets and glaciers flow, fracture, and melt &mdash; and how they will shape sea level over the coming century.</p>

          <p>Our work combines field and satellite geophysics with numerical modeling. We develop multi-element radar systems to image the interior and bed of glaciers, use satellite altimetry and stereo imagery to measure how ice and the land surface are changing, and build finite-element models of ice flow, firn compaction, and ocean-driven melt to interpret what we observe.</p>

          <p>Closer to home, we study relative sea-level change along the Gulf Coast, combining InSAR, GNSS, and poromechanical models to map and project vertical land motion &mdash; and we work with local partners to turn those projections into tools people can plan with.</p>

          <p>We are committed to open, collaborative, and reproducible science, and to building a research group where people from many backgrounds can do their best work.</p>
        </div>
    design:
      columns: '1'

  # ===== TEAM =====
  - block: people
    id: people
    content:
      title: Our Team
      text: ''
      # Filter and group team members by `user_groups` set in each author's profile.
      user_groups:
        - Principal Investigators
        - Postdoctoral Researchers
        - Graduate Students
        - Undergraduate Students
        - Research Staff
        - Alumni
    design:
      show_interests: false
      show_role: true
      show_social: true

  # ===== NEWS =====
  - block: collection
    id: news
    content:
      title: News
      subtitle: ''
      text: ''
      count: 4
      filters:
        folders:
          - post
    design:
      view: compact
      columns: '2'

  - block: markdown
    id: news_more
    content:
      title: ''
      text: |
        <p style="text-align:center; margin-top:-2rem;"><a href="/post/">View all news &rarr;</a></p>
    design:
      columns: '1'

  # ===== RESEARCH =====
  - block: markdown
    id: research
    content:
      title: Research
      text: |
        <div class="research-carousel">

          <div class="research-slide active">
            <h2 class="research-slide-title">Ice Flow</h2>
            <p class="research-slide-body">Englacial stresses cause ice to creep internally, with rates that depend strongly on temperature and on the evolving microstructure of crystal grains. We model glacier and ice-sheet motion to understand how the englacial viscosity of the ice sheet and assumptions about slip at the ice-base interface affect glacier retreat. Using the finite element method and models like Elmer/Ice and icepack, we solve equations that describe glacier flow and use some of the unique data our group collects to constrain the physical processes that contribute to motion.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Multi-Element Radar</h2>
            <p class="research-slide-body">We develop and use multi-element radar systems to image the internal structure, englacial properties, and basal conditions of glaciers and ice sheets. These systems can geolocate off-nadir energy and construct 3D images of the ice-base topography and the englacial structure of the ice sheet. Repeating these surveys, we perform multipass processing &mdash; combining repeat surveys, coregistering passes, and interfering the coregistered profiles to map vertical displacement, strain rates, and vertical velocity. These data provide distributed observations of englacial deformation that are under-used in ice-flow model initialization.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Firn</h2>
            <p class="research-slide-body">Firn is the porous snow layer that compacts into glacier ice. Firn density, temperature, and energy evolution shape surface elevation change and set the radar wave speed, which feeds directly into satellite altimetry and radar estimates of englacial structure. Our group builds firn models in a finite-element framework so that compaction, heat transport, and meltwater processes can be solved consistently and used with inverse methods to assimilate observations of compaction and initialize poorly constrained densification parameters. These constraints improve the interpretation of radar travel times and satellite altimetry trends, and can be used to reconstruct past climate from firn observations.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Submarine Ice-Shelf Melt</h2>
            <p class="research-slide-body">Warm, salty ocean water can circulate beneath ice shelves and melt them from below. Ice shelves float, so this melt does not raise sea level directly, but thinning reduces buttressing and can speed up the flow of grounded ice into the ocean. Our group develops methods that use time series of high-resolution stereo satellite imagery to map elevation change over floating ice. Repeated stereo DEMs are co-registered and differenced, then combined with estimates of englacial stresses and surface mass balance to isolate basal melt rates.</p>
          </div>

          <div class="research-slide">
            <h2 class="research-slide-title">Sea-Level Geophysics</h2>
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

          function goTo(n) {
            slides[current].classList.remove('active');
            document.querySelectorAll('#research .research-dot')[current].classList.remove('active');
            current = (n + slides.length) % slides.length;
            slides[current].classList.add('active');
            document.querySelectorAll('#research .research-dot')[current].classList.add('active');
          }

          document.querySelector('#research .research-prev').addEventListener('click', function() { goTo(current - 1); });
          document.querySelector('#research .research-next').addEventListener('click', function() { goTo(current + 1); });
        })();
        </script>
    design:
      columns: '1'

  # ===== PUBLICATIONS =====
  - block: collection
    id: publications
    content:
      title: Selected Publications
      text: |
        **For the full and most recent list, see [Google Scholar](https://scholar.google.com/citations?user=jf4jwlMAAAAJ).**
      count: 6
      filters:
        folders:
          - publication
    design:
      view: citation
      columns: '1'

  # ===== JOIN US =====
  - block: markdown
    id: join_us
    content:
      title: Join Us
      text: |
        <div class="opp-body">
          <p>We are always looking for curious, motivated people to join the group at every level &mdash; undergraduate, master's, PhD, and postdoctoral. We value people with a range of backgrounds in geophysics, glaciology, applied math, computation, engineering, and the physical sciences, and we care about building a supportive, inclusive group.</p>

          <p>If our work sounds interesting, please reach out &mdash; even when there is no specific posting, there are often opportunities. Read more about <a href="/opportunities/">opportunities and how to join</a>, or email <a href="mailto:ah301@rice.edu">ah301@rice.edu</a>.</p>
        </div>
    design:
      columns: '1'
---
