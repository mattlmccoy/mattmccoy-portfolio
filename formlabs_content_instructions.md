# Formlabs Technical Work - Content Instructions for Portfolio

This file contains synthesized information from Matt McCoy's technical papers written at Formlabs. Use this to update the portfolio website with accurate descriptions of his engineering work.

**Note:** Many of these papers are internal Formlabs documents. The general concepts and methodologies can be shared, but specific proprietary details should be generalized.

---

## CHUNK 1 - PROCESSED

### Paper 1: The Subtle Failures of Linear Regression (XY Scaling Tool)
**Platform:** Fuse 1, Fuse 1+, Next-gen SLS
**Date:** November 2022

**Summary:**
Developed the Fuse XY Scaling Tool calibration system and identified subtle failure modes in linear regression when applied to small datasets.

**Key Technical Contributions:**
- Designed a user-facing calibration tool that minimizes measurement burden (6 measurements per axis) while maintaining statistical validity
- Identified that floating y-intercept in linear regression causes failure modes:
  - Uniform error results in no scaling factor change
  - Middle feature errors create pivot points that are ignored
  - Opposite errors on small/large features can dramatically distort scaling factors
- Developed solution using fixed y-intercept regression and phantom points to improve accuracy
- Introduced concept of Outer Boundary Offset (OBO) to account for thermal bleed and spot size effects

**Skills Demonstrated:**
- Statistical analysis and regression techniques
- Calibration system design
- Edge case identification and testing methodology
- User-centered design (minimizing measurement requirements)

---

### Paper 2: 120W Laser - Print Time Analysis
**Platform:** Next-gen SLS
**Date:** March 2023
**Co-author:** Mehmet Dogan

**Summary:**
Comprehensive analysis of print time performance across different laser powers (30W-120W) and build volumes to determine optimal laser selection for next-generation SLS printers.

**Key Technical Contributions:**
- Developed Python-based print time estimation tool validated against PreForm and actual FLX timings
- Analyzed customer packing density data (median: 7-10%, 95th percentile: 20%, 99th percentile: 30%)
- Created cost-to-performance optimization framework mapping laser power to print time reduction
- Key findings:
  - 30W laser is nearly optimal for 165x165mm build area (Fuse 1 architecture)
  - 70W laser provides optimal cost-to-performance for larger build volumes (225mm+)
  - Interlayer time dominates print time more than laser power for smaller build areas
  - 33% improvement in interlayer time yields ~4 hour free speed improvement
- Compared trade-offs: 120W laser on 330x330mm bed is 23% faster but only 5.25 hours saved vs 30W

**Skills Demonstrated:**
- Python scripting for engineering analysis
- Customer data analysis and statistical modeling
- Cost-benefit analysis and optimization
- Systems-level thinking (understanding bottlenecks)

---

### Paper 3: 120W Laser - Catalog & Selection Summary
**Platform:** Next-gen SLS
**Date:** March 2023

**Summary:**
Comprehensive summary document synthesizing four major studies on high-power laser selection for next-generation SLS printing.

**Key Technical Contributions:**
- Integrated findings from: smoking/peak irradiance, print time, fine features, part quality, and mechanical properties studies
- **Final Recommendation:** 70W laser with 500μm spot size as optimal configuration
- Created decision framework balancing:
  - Peak irradiance process maps for smoking performance
  - Cost-to-throughput ratios based on customer data
  - Fine feature resolution requirements (0.6mm minimum)
  - Mechanical properties consistency

**Key Findings:**
- Mechanical properties remain consistent regardless of laser power (up to 3x higher peak irradiance than nominal)
- Fine feature resolution with 500μm spot falls within 50μm of Fuse 1+ performance
- Peak irradiance and print time analysis are primary drivers; part quality is secondary
- System can achieve 4x power increase without exceeding Fuse 1+ smoke levels using larger spot + reduced hatch

---

### Paper 4: 120W Laser - Smoking Performance and Peak Irradiance
**Platform:** Next-gen SLS
**Date:** March 2023

**Summary:**
Developed quantitative framework for predicting smoking performance based on peak irradiance, enabling future optical system selection without extensive experimentation.

**Key Technical Contributions:**
- Introduced **peak irradiance** [W/cm²] as key metric (previously not widely used at Formlabs SLS)
- Introduced **linear energy density** [mJ/cm] concept from academic L-PBF research
- Conducted 43+ experiments across spot sizes (300-650μm), powers (10-120W), and hatch spacings (150-260μm)
- Created binning criteria and lookup tables mapping peak irradiance to smoking performance levels:
  - No smoke
  - ≤ Fuse 1+ smoke (viable)
  - Between Fuse 1+ & ample smoke (viable with better air handling)
  - Ample gray smoke
  - Black smoke (not viable)
  - Combustion (catastrophic)

**Key Equations:**
- Peak Irradiance: I_peak = 2P / (πr²) where P = power, r = 1/e² spot radius
- Surface Energy Density (SED): Power / (Hatch Spacing × Galvo Speed)
- Linear Energy Density (LED): Power / Galvo Speed

**Critical Insight:**
- Reducing hatch spacing increases galvo speed → maintains SED but reduces LED → reduces smoking
- Larger spot + smaller hatch = lowest peak irradiance and best smoking performance
- 500μm spot with 150μm hatch can support up to 85-90W without exceeding acceptable smoke levels

**Skills Demonstrated:**
- Process physics understanding and characterization
- Development of predictive engineering tools
- Systematic experimental design
- Bridging academic research to industrial application

---

### Paper 5: The Measurable Impact of Thermal Uniformity
**Platform:** Fuse 1, Fuse 1+, Next-gen SLS
**Date:** July 2023

**Summary:**
Investigation correlating thermal uniformity across the print bed to print quality outcomes including mechanical properties and dimensional accuracy.

**Key Technical Contributions:**
- Developed test methodology using clustered z-tensile bars, bonusZ bars, and torque spinners across 9 discrete bed regions
- **Major Finding:** Path planning (how parts are drawn) can dominate printing process more than thermal uniformity
- Correlated metrics:
  - **Elongation at Break (EAB):** Strong correlation with thermal uniformity (6% center vs 4% cold regions)
  - **Z-scaling accuracy:** Correlated with thermal uniformity
  - **Moving assemblies/clearances:** Dominated by path planning, not thermal uniformity
  - **UTS and Modulus:** No correlation with location (set by bulk material properties)

**Key Insights:**
- Center of bed has most QT heater crosstalk → highest temperature → best EAB
- Lasing in view of IR sensor causes bed to print colder (sensor sees hot object → reduced heater duty cycle)
- For Fuse current state, thermal uniformity is important but not always dominating factor
- Path planning techniques (island hopping) could change this relationship

**Skills Demonstrated:**
- Experimental design for isolating variables
- Spatial mapping and data visualization
- Understanding of thermal systems and control loops
- Identifying confounding variables (path planning vs thermal effects)

---

## CHUNK 2 - PROCESSED

### Paper 6: Fuse Bed Temperature Fine Tuning Tool
**Platform:** Fuse 1, Fuse 1+
**Date:** 2022-2023

**Summary:**
Developed a comprehensive diagnostic and calibration tool for optimizing bed temperature across the Fuse SLS printer fleet. This tool has been widely adopted, including by notable users like Adam Savage on his Fuse 1+30W printer.

**Key Technical Contributions:**
- Created a printed diagnostic part with multiple assessment features:
  - **Torque Spinners:** Moving assemblies that test clearance performance across bed regions
  - **Dimpling Grid:** Visual indicators of over/under-sintering based on surface quality
  - **Birchbark Cones:** Texture assessment features showing powder adhesion characteristics
- Developed methodology to correlate visual/mechanical indicators with optimal bed temperature
- Established printer-to-printer comparison methodology for fleet calibration
- Created systematic approach to diagnose whether issues are thermal vs. other root causes

**Impact:**
- Tool widely deployed to customers and field engineers for printer diagnostics
- Featured in Adam Savage's Tested YouTube channel (demonstrating industry reach)
- Enabled non-expert users to diagnose and optimize printer performance

**Skills Demonstrated:**
- User-facing diagnostic tool design
- Multi-factor print quality assessment
- Fleet-wide calibration methodology
- Design for manufacturability (tool must print reliably on uncalibrated printers)

---

### Paper 7: Fuse User Scaling Calibration (XY Scaling Tool) - Detailed
**Platform:** Fuse 1, Fuse 1+
**Date:** 2022

**Summary:**
Comprehensive documentation of the user-facing XY scaling calibration system, improving dimensional accuracy from ±300μm to ±100μm through careful measurement methodology and statistical analysis.

**Key Technical Contributions:**
- **Complex vs. Naive Scaling:** Demonstrated why simple scaling factors fail and developed OBO-aware correction
- **Gage R&R Studies:** Conducted measurement system analysis to ensure reproducibility:
  - Quantified operator-to-operator variation
  - Established measurement technique guidelines
  - Validated caliper measurement methodology
- **SOP Development:** Created Standard Operating Procedure for consistent measurements:
  - Specified measurement locations on calibration part
  - Defined orientation and technique requirements
  - Established acceptance criteria

**Statistical Framework:**
- Achieved ±100μm tolerance (3x improvement over baseline ±300μm)
- 6 measurements per axis minimizes user burden while maintaining statistical validity
- Fixed y-intercept regression eliminates failure modes from floating intercept

**Skills Demonstrated:**
- Gage R&R and measurement system analysis
- SOP development for manufacturing consistency
- Statistical process control
- User experience optimization (minimal measurements, clear instructions)

---

### Paper 8: Minimum Optical Power Density for Nylon 12
**Platform:** Next-gen SLS
**Date:** March 2023

**Summary:**
Investigated the claimed minimum power density threshold (10⁴ W/cm²) for polymer sintering, proving that Nylon 12 can be successfully printed at power densities 30x lower than the industry-suggested minimum.

**Key Technical Contributions:**
- Tested power density range from 20,000 W/cm² down to 336 W/cm² while maintaining constant surface energy density (2500 mJ/cm²)
- **Major Finding:** Power density as low as 336 W/cm² successfully prints Nylon 12 with no degradation
- Surveyed power densities of commercial SLS printers and experimental systems:
  - Fuse 1+ 30W: ~20,571 W/cm²
  - Sinterit Lisa X: ~12,627 W/cm²
  - Fuse 1 (standard): ~11,014 W/cm²
  - Large spot experimental (800μm): ~2,520 W/cm²
  - Trumpf VCSEL arrays: 400-800 W/cm² (theoretical)
- Designed custom test geometry with fine features (0.4-1.0mm walls) to assess part strength at each power density
- Fine feature resolution showed no correlation with power density (variance dominated by cleaning process)

**Key Equation:**
- Power Density: I = P / (πr²) [W/cm²]

**Implications:**
- VCSEL (vertical-cavity surface-emitting laser) arrays are viable for SLS printing
- The 10⁴ W/cm² threshold does not apply to Nylon 12 with carbon black additive
- Opens design space for alternative optical systems (arrays vs. single galvo-steered laser)

**Skills Demonstrated:**
- Challenging industry assumptions with experimental evidence
- Systematic parameter sweeps with controlled variables
- Technology feasibility assessment for next-gen systems
- Bridging vendor claims to practical application

---

## CHUNK 3 - PROCESSED

### Paper 9: 800μm Large Spot Results (Variable Focus Project)
**Platform:** Next-gen SLS
**Date:** August-September 2022

**Summary:**
Investigated the feasibility of using larger laser spot sizes (800μm vs nominal 420μm) for next-generation SLS printers. This work supports the "variable focus" concept where a large spot fills bulk material while a small spot handles fine features and perimeters.

**Key Technical Contributions:**
- **Central Composite Design (CCD) Study:** Systematically varied hatch spacing (0.295-0.505mm) and galvo speed (1850-3850 mm/s) across 9 parameter sets
- **Beam Profiling:** Achieved ~800μm spot in both X and Y using additional optics (1/e² diameter: 825μm X, 793μm Y)
- **Major Results:**
  - **40% improvement in Z-EAB:** 6.5% vs nominal 4.6% at higher exposures
  - **Zero smoking:** No smoke generation even at 4000+ mJ/cm² energy density
  - **~10% speed improvement** at nominal exposure settings
  - **Minimal clouding:** ~2.8% power loss (acceptable)
  - **No dimpling** at high exposures with larger spot due to lower peak intensity

**Time Study Results (Full Build Volume):**
| Configuration | Spot (mm) | 10% PD (hr) | 30% PD (hr) |
|--------------|-----------|-------------|-------------|
| Fuse 1+ 30W | 0.420 | 2.98 | 6.79 |
| Nominal 840 (120W) | 0.840 | 0.94 | 1.84 |
| Nominal 1200 (120W) | 1.200 | 0.79 | 1.69 |

**Part Quality Assessment:**
- Fine feature resolution acceptable with proper parameter selection
- Best parameter set (L9): 0.400mm hatch, 2850 mm/s galvo, 2631 mJ/cm² SED
- Higher exposures possible without dimpling due to distributed energy

**Implications for Variable Focus:**
- Large spot can handle bulk material with higher energy → better mechanical properties
- Small spot handles perimeters and fine features → maintains resolution
- Combined approach enables faster printing with better properties and less smoke

**Skills Demonstrated:**
- Design of Experiments (Central Composite Design)
- Beam profiling and optical system characterization
- Multi-objective optimization (speed vs. quality vs. smoke)
- Technology feasibility studies for next-gen product development

---

## FILES STILL TO PROCESS (Chunks 4-5)

### Chunk 4 (~16MB):
- Decoupling Bed Temperature and Optical Power - Fuse Bed Temp Tool.pdf (16MB)

### Chunk 5 (12MB):
- 120W Laser - Part Quality and Fine Feature Performance.pdf (12MB)

### SKIPPED (Over 20MB limit):
- Fuse Bed Temperature Fine Tuning Tool.pdf (57MB) - Use compressed version instead

---

## OVERALL THEMES FOR PORTFOLIO

### Technical Expertise Areas:
1. **Laser-Material Interaction Physics**
   - Peak irradiance, linear energy density, surface energy density
   - Smoking/ablation characterization
   - Thermal effects on part quality

2. **Calibration System Design**
   - XY scaling calibration
   - Bed temperature fine tuning
   - Statistical methods for small datasets

3. **Process Optimization**
   - Print time analysis
   - Cost-to-performance optimization
   - Packing density effects

4. **Thermal Systems**
   - Thermal uniformity measurement and impact
   - Heater control systems
   - IR sensor feedback loops

5. **Data-Driven Decision Making**
   - Customer usage data analysis
   - Predictive modeling
   - Process maps and lookup tables

### Key Accomplishments to Highlight:
- Created tools that enable future engineering decisions without new experiments
- Bridged academic research concepts (linear energy density) to industrial application
- Developed user-facing calibration tools balancing accuracy with usability
- Systematic characterization of 120W laser viability for next-gen SLS
- Quantified relationships between process parameters and part quality
- Bed Temperature Tool adopted industry-wide (featured by Adam Savage)
- Challenged vendor assumptions with rigorous experimental evidence (power density study)
- Improved dimensional accuracy 3x through measurement system analysis (Gage R&R)

---

## PROMPT FOR NEXT SESSION

Copy and paste this prompt to continue processing in a new session:

```
Continue processing Formlabs papers for my portfolio website.

Context:
- I have an instruction file at: /Users/mattmccoy/Documents/personal/applications/resumes/portfolio/site/formlabs_content_instructions.md
- Papers already processed (Chunks 1-2): XY Scaling Tool, 120W Laser Print Time, 120W Laser Catalog Summary, Smoking Performance/Peak Irradiance, Thermal Uniformity Impact, Bed Temperature Fine Tuning Tool, User Scaling Calibration, Minimum Optical Power Density

Your task:
1. Read the existing instruction file to understand what's been captured
2. Process the remaining PDFs from /Users/mattmccoy/Documents/formlabs/papers_matt_wrote:
   - Chunk 3: 800um Large Spot Results (Variable Focus Project).pdf (5.5MB)
   - Chunk 4: Decoupling Bed Temperature and Optical Power - Fuse Bed Temp Tool.pdf (16MB)
   - Chunk 5: 120W Laser - Part Quality and Fine Feature Performance.pdf (12MB)
3. Update the instruction file with synthesized content from each chunk
4. After all PDFs are processed, generate a final prompt for updating the actual website

Important: Only process PDFs, skip .zip files and subdirectories with duplicates.
```

---

*Last updated: Chunk 3 complete (9 papers total)*

Additional information: there is a YouTube video of me giving a talk at a conference (Solid Freeform Fabrication Symposium 2025 in Austin, TX). This can be embedded as a video either under the low-cost diagnostics modal of my research or the RFAM modal (https://youtu.be/b4yTXEDQ0zk). Also, I'm going to link my PhD Proposal Presentation as well (https://youtu.be/Hb7Ml6X2GxU) which can be embedded as a video as well. Further, I'm linking my PhD Proposal Slides so people can view those if interested (https://docs.google.com/presentation/d/1a9rlaCXvCfr2C6LK6zRw-2JO90qCgkmNeJUSctIsVUY/edit?usp=sharing). Also, it would be nice to host my PhD Proposal document somewhere on the site as well which can be found at /Users/mattmccoy/GaTech Dropbox/Matthew McCoy/mattmccoy-research/research/dissertation_materials/proposal/writing/drafts/mccoy_proposal_v10_2025-08-23_1714_compressed.pdf.

Also, for fun side projects, we built the automatic bottle opener back in college (so currently hosted in archives). Here are some links for it: we have the Hackaday feature (article: https://hackaday.com/2020/12/18/over-engineered-bottle-opener-takes-the-drudgery-out-of-drinking/; podcast: https://hackaday.com/2020/12/24/hackaday-podcast-099-our-hundredth-episode-denture-synth-oled-keycaps-and-snes-raytracing/), the actual video (https://youtu.be/XNhSrVIV6Ac?si=KFDt04dXpobJUNAB), the manufacturing video (https://youtu.be/koXtxFYrNRM?si=-Sv3RfxTZsTGyNC6), and the quick highlight video (https://youtu.be/1FEmYQiFS-Y?si=RY8HUpdr7qsNxx50). I think it would be nice to make this project more prominent since it's somewhat buried right now in one of the subpage modals.

I'm also adding some additional pictures under /images/content. They are mostly Formlabs (full-time) related. One of my favorites is the Bed Temp Tuning Tool because it's used so widely so much so that Adam Savage himself uses it on his Fuse 1+30W printer! Here's the YouTube video (https://www.youtube.com/watch?v=x78bJi-snrc) and the picture is named adam-savage-bedtemptool. I also added a bunch of pictures that the names of them should be descriptive enough for you to pair with the information you've extracted from the Formlabs documents.