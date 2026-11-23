# Synthetic BRSR Demo

`sample_brsr_demo.pdf` is a fictional four-page disclosure for testing VeriGreen's PDF upload, claim extraction, evidence retrieval, and scoring flow. It is not a real company report, a SEBI filing, or investment advice.

## Expected inconsistencies

These values are deliberately inconsistent so an audit has examples to flag:

- **Water reuse (page 2):** Narrative says 75%; the table gives 86,000 kL reused out of 126,000 kL withdrawn, about 68%.
- **Workplace safety (page 3):** Narrative says zero lost-time injuries; the incident register lists three.
- **Grievances (pages 3-4):** Narrative reports 97% closed; the register says 31 of 34, about 91%.
- **Board independence (page 4):** The CEO describes all five board members as independent; the board register lists one independent director.
- **Supplier screening (page 4):** Chair's message says all suppliers were screened; the table says 312 of 400, or 78%.

Regenerate the PDF from this directory with:

```bash
../backend/.venv/bin/python generate_demo_brsr.py
```
