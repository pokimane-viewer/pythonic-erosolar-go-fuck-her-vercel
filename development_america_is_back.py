import os, json, random
from flask import Flask, render_template_string, Response, request, send_from_directory
import pandas as pd, numpy as np, sqlite3
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DB_PATH = "eos.db"
REF_JSON = "documents.json"

DATA = [
  {"executive_order_number":14147,"title":"Ending the Weaponization of the Federal Government","html_url":"https://www.federalregister.gov/documents/2025/01/28/2025-01900/ending-the-weaponization-of-the-federal-government","status":"issued"},
  {"executive_order_number":14148,"title":"Initial Rescissions of Harmful Executive Orders and Actions","html_url":"https://www.federalregister.gov/documents/2025/01/28/2025-01901/initial-rescissions-of-harmful-executive-orders-and-actions","status":"issued"},
  {"executive_order_number":14149,"title":"Restoring Freedom of Speech and Ending Federal Censorship","html_url":"https://www.federalregister.gov/documents/2025/01/28/2025-01902/restoring-freedom-of-speech-and-ending-federal-censorship","status":"issued"},
  {"executive_order_number":14150,"title":"America First Policy Directive to the Secretary of State","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-01952/america-first-policy-directive-to-the-secretary-of-state","status":"issued"},
  {"executive_order_number":14151,"title":"Ending Radical and Wasteful Government DEI Programs and Preferencing","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-01953/ending-radical-and-wasteful-government-dei-programs-and-preferencing","status":"paused","rejection_date":"2025-02-21","rejection_link":"https://www.morganlewis.com/pubs/2025/02/federal-judge-temporarily-halts-enforcement-of-executive-orders-related-to-dei"},
  {"executive_order_number":14152,"title":"Holding Former Government Officials Accountable for Election Interference and Improper Disclosure of Sensitive Governmental Information","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-01954/holding-former-government-officials-accountable-for-election-interference-and-improper-disclosure","status":"issued"},
  {"executive_order_number":14153,"title":"Unleashing Alaska's Extraordinary Resource Potential","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-01955/unleashing-alaskas-extraordinary-resource-potential","status":"issued"},
  {"executive_order_number":14154,"title":"Unleashing American Energy","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-01956/unleashing-american-energy","status":"issued"},
  {"executive_order_number":14155,"title":"Withdrawing the United States From the World Health Organization","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-01957/withdrawing-the-united-states-from-the-world-health-organization","status":"issued"},
  {"executive_order_number":14156,"title":"Declaring a National Energy Emergency","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-02003/declaring-a-national-energy-emergency","status":"issued"},
  {"executive_order_number":14157,"title":"Designating Cartels and Other Organizations as Foreign Terrorist Organizations and Specially Designated Global Terrorists","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-02004/designating-cartels-and-other-organizations-as-foreign-terrorist-organizations-and-specially","status":"issued"},
  {"executive_order_number":14158,"title":"Establishing and Implementing the President's \"Department of Government Efficiency\"","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-02005/establishing-and-implementing-the-presidents-department-of-government-efficiency","status":"issued"},
  {"executive_order_number":14159,"title":"Protecting the American People Against Invasion","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-02006/protecting-the-american-people-against-invasion","status":"issued"},
  {"executive_order_number":14160,"title":"Protecting the Meaning and Value of American Citizenship","html_url":"https://www.federalregister.gov/documents/2025/01/29/2025-02007/protecting-the-meaning-and-value-of-american-citizenship","status":"paused","rejection_date":"2025-02-05","rejection_link":"https://ogletree.com/insights-resources/blog-posts/trump-2-0-first-two-months-in-review-a-summary-of-immigration-related-actions"},
  {"executive_order_number":14161,"title":"Protecting the United States From Foreign Terrorists and Other National Security and Public Safety Threats","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02009/protecting-the-united-states-from-foreign-terrorists-and-other-national-security-and-public-safety","status":"issued"},
  {"executive_order_number":14162,"title":"Putting America First in International Environmental Agreements","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02010/putting-america-first-in-international-environmental-agreements","status":"issued"},
  {"executive_order_number":14163,"title":"Realigning the United States Refugee Admissions Program","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02011/realigning-the-united-states-refugee-admissions-program","status":"issued"},
  {"executive_order_number":14164,"title":"Restoring the Death Penalty and Protecting Public Safety","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02012/restoring-the-death-penalty-and-protecting-public-safety","status":"issued"},
  {"executive_order_number":14165,"title":"Securing Our Borders","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02015/securing-our-borders","status":"issued"},
  {"executive_order_number":14166,"title":"Application of Protecting Americans From Foreign Adversary Controlled Applications Act to TikTok","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02087/application-of-protecting-americans-from-foreign-adversary-controlled-applications-act-to-tiktok","status":"issued"},
  {"executive_order_number":14167,"title":"Clarifying the Military's Role in Protecting the Territorial Integrity of the United States","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02089/clarifying-the-militarys-role-in-protecting-the-territorial-integrity-of-the-united-states","status":"issued"},
  {"executive_order_number":14168,"title":"Defending Women From Gender Ideology Extremism and Restoring Biological Truth to the Federal Government","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02090/defending-women-from-gender-ideology-extremism-and-restoring-biological-truth-to-the-federal","status":"paused","rejection_date":"2025-02-18","rejection_link":"https://rbgg.com/transgender-women-file-suit-against-bop-challenging-trump-policy-terminating-medical-care-and-moving-them-to-mens-prisons"},
  {"executive_order_number":14169,"title":"Reevaluating and Realigning United States Foreign Aid","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02091/reevaluating-and-realigning-united-states-foreign-aid","status":"paused","rejection_date":"2025-02-25","rejection_link":"https://ogletree.com/insights-resources/blog-posts/trump-2-0-first-two-months-in-review-a-summary-of-immigration-related-actions"},
  {"executive_order_number":14170,"title":"Reforming the Federal Hiring Process and Restoring Merit to Government Service","html_url":"https://www.federalregister.gov/documents/2025/01/30/2025-02094/reforming-the-federal-hiring-process-and-restoring-merit-to-government-service","status":"issued"},
  {"executive_order_number":14171,"title":"Restoring Accountability to Policy-Influencing Positions Within the Federal Workforce","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02095/restoring-accountability-to-policy-influencing-positions-within-the-federal-workforce","status":"issued"},
  {"executive_order_number":14172,"title":"Restoring Names That Honor American Greatness","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02096/restoring-names-that-honor-american-greatness","status":"issued"},
  {"executive_order_number":14173,"title":"Ending Illegal Discrimination and Restoring Merit-Based Opportunity","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02097/ending-illegal-discrimination-and-restoring-merit-based-opportunity","status":"paused","rejection_date":"2025-02-21","rejection_link":"https://www.morganlewis.com/pubs/2025/02/federal-judge-temporarily-halts-enforcement-of-executive-orders-related-to-dei"},
  {"executive_order_number":14174,"title":"Revocation of Certain Executive Orders","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02098/revocation-of-certain-executive-orders","status":"issued"},
  {"executive_order_number":14175,"title":"Designation of Ansar Allah as a Foreign Terrorist Organization","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02103/designation-of-ansar-allah-as-a-foreign-terrorist-organization","status":"issued"},
  {"executive_order_number":14176,"title":"Declassification of Records Concerning the Assassinations of President John F. Kennedy, Senator Robert F. Kennedy, and the Reverend Dr. Martin Luther King, Jr.","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02116/declassification-of-records-concerning-the-assassinations-of-president-john-f-kennedy-senator","status":"issued"},
  {"executive_order_number":14177,"title":"President's Council of Advisors on Science and Technology","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02121/presidents-council-of-advisors-on-science-and-technology","status":"issued"},
  {"executive_order_number":14178,"title":"Strengthening American Leadership in Digital Financial Technology","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02123/strengthening-american-leadership-in-digital-financial-technology","status":"issued"},
  {"executive_order_number":14179,"title":"Removing Barriers to American Leadership in Artificial Intelligence","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02172/removing-barriers-to-american-leadership-in-artificial-intelligence","status":"issued"},
  {"executive_order_number":14180,"title":"Council To Assess the Federal Emergency Management Agency","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02173/council-to-assess-the-federal-emergency-management-agency","status":"issued"},
  {"executive_order_number":14181,"title":"Emergency Measures To Provide Water Resources in California and Improve Disaster Response in Certain Areas","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02174/emergency-measures-to-provide-water-resources-in-california-and-improve-disaster-response-in-certain","status":"issued"},
  {"executive_order_number":14182,"title":"Enforcing the Hyde Amendment","html_url":"https://www.federalregister.gov/documents/2025/01/31/2025-02175/enforcing-the-hyde-amendment","status":"issued"},
  {"executive_order_number":14183,"title":"Prioritizing Military Excellence and Readiness","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02178/prioritizing-military-excellence-and-readiness","status":"issued"},
  {"executive_order_number":14184,"title":"Reinstating Service Members Discharged Under the Military's COVID-19 Vaccination Mandate","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02180/reinstating-service-members-discharged-under-the-militarys-covid-19-vaccination-mandate","status":"issued"},
  {"executive_order_number":14185,"title":"Restoring America's Fighting Force","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02181/restoring-americas-fighting-force","status":"issued"},
  {"executive_order_number":14186,"title":"The Iron Dome for America","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02182/the-iron-dome-for-america","status":"issued"},
  {"executive_order_number":14187,"title":"Protecting Children From Chemical and Surgical Mutilation","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02194/protecting-children-from-chemical-and-surgical-mutilation","status":"paused","rejection_date":"2025-02-14","rejection_link":"https://www.shipmangoodwin.com/insights/two-federal-courts-issue-injunctions-temporarily-blocking-trumps-executive-order-restricting-access-to-gender-affirming-care.html"},
  {"executive_order_number":14188,"title":"Additional Measures To Combat Anti-Semitism","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02230/additional-measures-to-combat-anti-semitism","status":"issued"},
  {"executive_order_number":14189,"title":"Celebrating America's 250th Birthday","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02231/celebrating-americas-250th-birthday","status":"issued"},
  {"executive_order_number":14190,"title":"Ending Radical Indoctrination in K-12 Schooling","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02232/ending-radical-indoctrination-in-k-12-schooling","status":"paused","rejection_date":"2025-04-24","rejection_link":"https://abcnews.go.com/US/judge-partially-blocks-trumps-effort-ban-dei-12/story?id=121131844"},
  {"executive_order_number":14191,"title":"Expanding Educational Freedom and Opportunity for Families","html_url":"https://www.federalregister.gov/documents/2025/02/03/2025-02233/expanding-educational-freedom-and-opportunity-for-families","status":"issued"},
  {"executive_order_number":14192,"title":"Unleashing Prosperity Through Deregulation","html_url":"https://www.federalregister.gov/documents/2025/02/06/2025-02345/unleashing-prosperity-through-deregulation","status":"issued"},
  {"executive_order_number":14193,"title":"Imposing Duties To Address the Flow of Illicit Drugs Across Our Northern Border","html_url":"https://www.federalregister.gov/documents/2025/02/07/2025-02406/imposing-duties-to-address-the-flow-of-illicit-drugs-across-our-northern-border","status":"issued"},
  {"executive_order_number":14194,"title":"Imposing Duties To Address the Situation at Our Southern Border","html_url":"https://www.federalregister.gov/documents/2025/02/07/2025-02407/imposing-duties-to-address-the-situation-at-our-southern-border","status":"issued"},
  {"executive_order_number":14195,"title":"Imposing Duties To Address the Synthetic Opioid Supply Chain in the People's Republic of China","html_url":"https://www.federalregister.gov/documents/2025/02/07/2025-02408/imposing-duties-to-address-the-synthetic-opioid-supply-chain-in-the-peoples-republic-of-china","status":"issued"},
  {"executive_order_number":14196,"title":"A Plan for Establishing a United States Sovereign Wealth Fund","html_url":"https://www.federalregister.gov/documents/2025/02/10/2025-02477/a-plan-for-establishing-a-united-states-sovereign-wealth-fund","status":"issued"},
  {"executive_order_number":14197,"title":"Progress on the Situation at Our Northern Border","html_url":"https://www.federalregister.gov/documents/2025/02/10/2025-02478/progress-on-the-situation-at-our-northern-border","status":"issued"},
  {"executive_order_number":14198,"title":"Progress on the Situation at Our Southern Border","html_url":"https://www.federalregister.gov/documents/2025/02/10/2025-02479/progress-on-the-situation-at-our-southern-border","status":"issued"},
  {"executive_order_number":14199,"title":"Withdrawing the United States From and Ending Funding to Certain United Nations Organizations and Reviewing United States Support to All International Organizations","html_url":"https://www.federalregister.gov/documents/2025/02/10/2025-02504/withdrawing-the-united-states-from-and-ending-funding-to-certain-united-nations-organizations-and","status":"issued"},
  {"executive_order_number":14200,"title":"Amendment to Duties Addressing the Synthetic Opioid Supply Chain in the People's Republic of China","html_url":"https://www.federalregister.gov/documents/2025/02/11/2025-02512/amendment-to-duties-addressing-the-synthetic-opioid-supply-chain-in-the-peoples-republic-of-china","status":"issued"},
  {"executive_order_number":14201,"title":"Keeping Men Out of Women's Sports","html_url":"https://www.federalregister.gov/documents/2025/02/11/2025-02513/keeping-men-out-of-womens-sports","status":"issued"},
  {"executive_order_number":14202,"title":"Eradicating Anti-Christian Bias","html_url":"https://www.federalregister.gov/documents/2025/02/12/2025-02611/eradicating-anti-christian-bias","status":"issued"},
  {"executive_order_number":14203,"title":"Imposing Sanctions on the International Criminal Court","html_url":"https://www.federalregister.gov/documents/2025/02/12/2025-02612/imposing-sanctions-on-the-international-criminal-court","status":"issued"},
  {"executive_order_number":14204,"title":"Addressing Egregious Actions of the Republic of South Africa","html_url":"https://www.federalregister.gov/documents/2025/02/12/2025-02630/addressing-egregious-actions-of-the-republic-of-south-africa","status":"issued"},
  {"executive_order_number":14205,"title":"Establishment of the White House Faith Office","html_url":"https://www.federalregister.gov/documents/2025/02/12/2025-02635/establishment-of-the-white-house-faith-office","status":"issued"},
  {"executive_order_number":14206,"title":"Protecting Second Amendment Rights","html_url":"https://www.federalregister.gov/documents/2025/02/12/2025-02636/protecting-second-amendment-rights","status":"issued"},
  {"executive_order_number":14207,"title":"Eliminating the Federal Executive Institute","html_url":"https://www.federalregister.gov/documents/2025/02/14/2025-02734/eliminating-the-federal-executive-institute","status":"issued"},
  {"executive_order_number":14208,"title":"Ending Procurement and Forced Use of Paper Straws","html_url":"https://www.federalregister.gov/documents/2025/02/14/2025-02735/ending-procurement-and-forced-use-of-paper-straws","status":"issued"},
  {"executive_order_number":14209,"title":"Pausing Foreign Corrupt Practices Act Enforcement To Further American Economic and National Security","html_url":"https://www.federalregister.gov/documents/2025/02/14/2025-02736/pausing-foreign-corrupt-practices-act-enforcement-to-further-american-economic-and-national-security","status":"issued"},
  {"executive_order_number":14210,"title":"Implementing the President's \"Department of Government Efficiency\" Workforce Optimization Initiative","html_url":"https://www.federalregister.gov/documents/2025/02/14/2025-02762/implementing-the-presidents-department-of-government-efficiency-workforce-optimization-initiative","status":"issued"},
  {"executive_order_number":14211,"title":"One Voice for America's Foreign Relations","html_url":"https://www.federalregister.gov/documents/2025/02/18/2025-02841/one-voice-for-americas-foreign-relations","status":"issued"},
  {"executive_order_number":14212,"title":"Establishing the President's Make America Healthy Again Commission","html_url":"https://www.federalregister.gov/documents/2025/02/19/2025-02871/establishing-the-presidents-make-america-healthy-again-commission","status":"issued"},
  {"executive_order_number":14213,"title":"Establishing the National Energy Dominance Council","html_url":"https://www.federalregister.gov/documents/2025/02/20/2025-02928/establishing-the-national-energy-dominance-council","status":"issued"},
  {"executive_order_number":14214,"title":"Keeping Education Accessible and Ending COVID-19 Vaccine Mandates in Schools","html_url":"https://www.federalregister.gov/documents/2025/02/20/2025-02931/keeping-education-accessible-and-ending-covid-19-vaccine-mandates-in-schools","status":"issued"},
  {"executive_order_number":14215,"title":"Ensuring Accountability for All Agencies","html_url":"https://www.federalregister.gov/documents/2025/02/24/2025-03063/ensuring-accountability-for-all-agencies","status":"issued"},
  {"executive_order_number":14216,"title":"Expanding Access to In Vitro Fertilization","html_url":"https://www.federalregister.gov/documents/2025/02/24/2025-03064/expanding-access-to-in-vitro-fertilization","status":"issued"},
  {"executive_order_number":14217,"title":"Commencing the Reduction of the Federal Bureaucracy","html_url":"https://www.federalregister.gov/documents/2025/02/25/2025-03133/commencing-the-reduction-of-the-federal-bureaucracy","status":"issued"},
  {"executive_order_number":14218,"title":"Ending Taxpayer Subsidization of Open Borders","html_url":"https://www.federalregister.gov/documents/2025/02/25/2025-03137/ending-taxpayer-subsidization-of-open-borders","status":"issued"},
  {"executive_order_number":14219,"title":"Ensuring Lawful Governance and Implementing the President's \"Department of Government Efficiency\" Deregulatory Initiative","html_url":"https://www.federalregister.gov/documents/2025/02/25/2025-03138/ensuring-lawful-governance-and-implementing-the-presidents-department-of-government-efficiency","status":"issued"},
  {"executive_order_number":14220,"title":"Addressing the Threat to National Security From Imports of Copper","html_url":"https://www.federalregister.gov/documents/2025/02/28/2025-03439/addressing-the-threat-to-national-security-from-imports-of-copper","status":"issued"},
  {"executive_order_number":14221,"title":"Making America Healthy Again by Empowering Patients With Clear, Accurate, and Actionable Healthcare Pricing Information","html_url":"https://www.federalregister.gov/documents/2025/02/28/2025-03440/making-america-healthy-again-by-empowering-patients-with-clear-accurate-and-actionable-healthcare","status":"issued"},
  {"executive_order_number":14222,"title":"Implementing the President's \"Department of Government Efficiency\" Cost Efficiency Initiative","html_url":"https://www.federalregister.gov/documents/2025/03/03/2025-03527/implementing-the-presidents-department-of-government-efficiency-cost-efficiency-initiative","status":"issued"},
  {"executive_order_number":14223,"title":"Addressing the Threat to National Security From Imports of Timber, Lumber, and Their Derivative Products","html_url":"https://www.federalregister.gov/documents/2025/03/06/2025-03693/addressing-the-threat-to-national-security-from-imports-of-timber-lumber-and-their-derivative-products","status":"issued"},
  {"executive_order_number":14224,"title":"Designating English as the Official Language of the United States","html_url":"https://www.federalregister.gov/documents/2025/03/06/2025-03694/designating-english-as-the-official-language-of-the-united-states","status":"issued"},
  {"executive_order_number":14225,"title":"Immediate Expansion of American Timber Production","html_url":"https://www.federalregister.gov/documents/2025/03/06/2025-03695/immediate-expansion-of-american-timber-production","status":"issued"},
  {"executive_order_number":14226,"title":"Amendment to Duties To Address the Flow of Illicit Drugs Across Our Northern Border","html_url":"https://www.federalregister.gov/documents/2025/03/06/2025-03728/amendment-to-duties-to-address-the-flow-of-illicit-drugs-across-our-northern-border","status":"issued"},
  {"executive_order_number":14227,"title":"Amendment to Duties To Address the Situation at Our Southern Border","html_url":"https://www.federalregister.gov/documents/2025/03/06/2025-03729/amendment-to-duties-to-address-the-situation-at-our-southern-border","status":"issued"},
  {"executive_order_number":14228,"title":"Further Amendment to Duties Addressing the Synthetic Opioid Supply Chain in the People's Republic of China","html_url":"https://www.federalregister.gov/documents/2025/03/07/2025-03775/further-amendment-to-duties-addressing-the-synthetic-opioid-supply-chain-in-the-peoples-republic-of","status":"issued"},
  {"executive_order_number":14229,"title":"Honoring Jocelyn Nungaray","html_url":"https://www.federalregister.gov/documents/2025/03/10/2025-03869/honoring-jocelyn-nungaray","status":"issued"},
  {"executive_order_number":14230,"title":"Addressing Risks From Perkins Coie LLP","html_url":"https://www.federalregister.gov/documents/2025/03/11/2025-03989/addressing-risks-from-perkins-coie-llp","status":"issued"},
  {"executive_order_number":14231,"title":"Amendment to Duties To Address the Flow of Illicit Drugs Across Our Northern Border","html_url":"https://www.federalregister.gov/documents/2025/03/11/2025-03990/amendment-to-duties-to-address-the-flow-of-illicit-drugs-across-our-northern-border","status":"issued"},
  {"executive_order_number":14232,"title":"Amendment to Duties To Address the Flow of Illicit Drugs Across Our Southern Border","html_url":"https://www.federalregister.gov/documents/2025/03/11/2025-03991/amendment-to-duties-to-address-the-flow-of-illicit-drugs-across-our-southern-border","status":"issued"},
  {"executive_order_number":14233,"title":"Establishment of the Strategic Bitcoin Reserve and United States Digital Asset Stockpile","html_url":"https://www.federalregister.gov/documents/2025/03/11/2025-03992/establishment-of-the-strategic-bitcoin-reserve-and-united-states-digital-asset-stockpile","status":"issued"},
  {"executive_order_number":14234,"title":"Establishing the White House Task Force on the FIFA World Cup 2026","html_url":"https://www.federalregister.gov/documents/2025/03/12/2025-04102/establishing-the-white-house-task-force-on-the-fifa-world-cup-2026","status":"issued"},
  {"executive_order_number":14235,"title":"Restoring Public Service Loan Forgiveness","html_url":"https://www.federalregister.gov/documents/2025/03/12/2025-04103/restoring-public-service-loan-forgiveness","status":"issued"},
  {"executive_order_number":14236,"title":"Additional Rescissions of Harmful Executive Orders and Actions","html_url":"https://www.federalregister.gov/documents/2025/03/20/2025-04866/additional-rescissions-of-harmful-executive-orders-and-actions","status":"issued"},
  {"executive_order_number":14237,"title":"Addressing Risks From Paul Weiss","html_url":"https://www.federalregister.gov/documents/2025/03/20/2025-04867/addressing-risks-from-paul-weiss","status":"blocked","rejection_date":"2025-03-21","rejection_link":"https://www.federalregister.gov/presidential-documents/executive-orders/donald-trump/2025"},
  {"executive_order_number":14238,"title":"Continuing the Reduction of the Federal Bureaucracy","html_url":"https://www.federalregister.gov/documents/2025/03/20/2025-04868/continuing-the-reduction-of-the-federal-bureaucracy","status":"issued"},
  {"executive_order_number":14239,"title":"Achieving Efficiency Through State and Local Preparedness","html_url":"https://www.federalregister.gov/documents/2025/03/21/2025-04973/achieving-efficiency-through-state-and-local-preparedness","status":"issued"},
  {"executive_order_number":14240,"title":"Eliminating Waste and Saving Taxpayer Dollars by Consolidating Procurement","html_url":"https://www.federalregister.gov/documents/2025/03/25/2025-05197/eliminating-waste-and-saving-taxpayer-dollars-by-consolidating-procurement","status":"issued"},
  {"executive_order_number":14241,"title":"Immediate Measures To Increase American Mineral Production","html_url":"https://www.federalregister.gov/documents/2025/03/25/2025-05212/immediate-measures-to-increase-american-mineral-production","status":"issued"},
  {"executive_order_number":14242,"title":"Improving Education Outcomes by Empowering Parents, States, and Communities","html_url":"https://www.federalregister.gov/documents/2025/03/25/2025-05213/improving-education-outcomes-by-empowering-parents-states-and-communities","status":"issued"},
  {"executive_order_number":14243,"title":"Stopping Waste, Fraud, and Abuse by Eliminating Information Silos","html_url":"https://www.federalregister.gov/documents/2025/03/25/2025-05214/stopping-waste-fraud-and-abuse-by-eliminating-information-silos","status":"issued"},
  {"executive_order_number":14244,"title":"Addressing Remedial Action by Paul Weiss","html_url":"https://www.federalregister.gov/documents/2025/03/26/2025-05291/addressing-remedial-action-by-paul-weiss","status":"issued"},
  {"executive_order_number":14245,"title":"Imposing Tariffs on Countries Importing Venezuelan Oil","html_url":"https://www.federalregister.gov/documents/2025/03/27/2025-05440/imposing-tariffs-on-countries-importing-venezuelan-oil","status":"issued"},
  {"executive_order_number":14246,"title":"Addressing Risks From Jenner & Block","html_url":"https://www.federalregister.gov/documents/2025/03/28/2025-05519/addressing-risks-from-jenner--block","status":"issued"},
  {"executive_order_number":14247,"title":"Modernizing Payments To and From America's Bank Account","html_url":"https://www.federalregister.gov/documents/2025/03/28/2025-05522/modernizing-payments-to-and-from-americas-bank-account","status":"issued"},
  {"executive_order_number":14248,"title":"Preserving and Protecting the Integrity of American Elections","html_url":"https://www.federalregister.gov/documents/2025/03/28/2025-05523/preserving-and-protecting-the-integrity-of-american-elections","status":"paused","rejection_date":"2025-04-24","rejection_link":"https://www.reuters.com/world/us/judge-partly-blocks-trump-order-seeking-overhaul-us-elections-2025-04-24/"},
  {"executive_order_number":14249,"title":"Protecting America's Bank Account Against Fraud, Waste, and Abuse","html_url":"https://www.federalregister.gov/documents/2025/03/28/2025-05524/protecting-americas-bank-account-against-fraud-waste-and-abuse","status":"issued"},
  {"executive_order_number":14250,"title":"Addressing Risks From WilmerHale","html_url":"https://www.federalregister.gov/documents/2025/04/03/2025-05845/addressing-risks-from-wilmerhale","status":"issued"},
  {"executive_order_number":14251,"title":"Exclusions From Federal Labor-Management Relations Programs","html_url":"https://www.federalregister.gov/documents/2025/04/03/2025-05836/exclusions-from-federal-labor-management-relations-programs","status":"issued"},
  {"executive_order_number":14252,"title":"Making the District of Columbia Safe and Beautiful","html_url":"https://www.federalregister.gov/documents/2025/04/03/2025-05837/making-the-district-of-columbia-safe-and-beautiful","status":"issued"},
  {"executive_order_number":14253,"title":"Restoring Truth and Sanity to American History","html_url":"https://www.federalregister.gov/documents/2025/04/03/2025-05838/restoring-truth-and-sanity-to-american-history","status":"issued"},
  {"executive_order_number":14254,"title":"Combating Unfair Practices in the Live Entertainment Market","html_url":"https://www.federalregister.gov/documents/2025/04/03/2025-05906/combating-unfair-practices-in-the-live-entertainment-market","status":"issued"},
  {"executive_order_number":14255,"title":"Establishing the United States Investment Accelerator","html_url":"https://www.federalregister.gov/documents/2025/04/03/2025-05908/establishing-the-united-states-investment-accelerator","status":"issued"},
  {"executive_order_number":14256,"title":"Further Amendment to Duties Addressing the Synthetic Opioid Supply Chain in the People's Republic of China as Applied to Low-Value Imports","html_url":"https://www.federalregister.gov/documents/2025/04/07/2025-06027/further-amendment-to-duties-addressing-the-synthetic-opioid-supply-chain-in-the-peoples-republic-of","status":"issued"},
  {"executive_order_number":14257,"title":"Regulating Imports With a Reciprocal Tariff To Rectify Trade Practices That Contribute to Large and Persistent Annual United States Goods Trade Deficits","html_url":"https://www.federalregister.gov/documents/2025/04/07/2025-06063/regulating-imports-with-a-reciprocal-tariff-to-rectify-trade-practices-that-contribute-to-large-and","status":"issued"},
  {"executive_order_number":14258,"title":"Extending the TikTok Enforcement Delay","html_url":"https://www.federalregister.gov/documents/2025/04/09/2025-06162/extending-the-tiktok-enforcement-delay","status":"issued"},
  {"executive_order_number":14259,"title":"Amendment to Reciprocal Tariffs and Updated Duties as Applied to Low-Value Imports From the People's Republic of China","html_url":"https://www.federalregister.gov/documents/2025/04/14/2025-06378/amendment-to-reciprocal-tariffs-and-updated-duties-as-applied-to-low-value-imports-from-the-peoples","status":"issued"},
  {"executive_order_number":14260,"title":"Protecting American Energy From State Overreach","html_url":"https://www.federalregister.gov/documents/2025/04/14/2025-06379/protecting-american-energy-from-state-overreach","status":"issued"},
  {"executive_order_number":14261,"title":"Reinvigorating America's Beautiful Clean Coal Industry and Amending Executive Order 14241","html_url":"https://www.federalregister.gov/documents/2025/04/14/2025-06380/reinvigorating-americas-beautiful-clean-coal-industry-and-amending-executive-order-14241","status":"issued"},
  {"executive_order_number":14262,"title":"Strengthening the Reliability and Security of the United States Electric Grid","html_url":"https://www.federalregister.gov/documents/2025/04/14/2025-06381/strengthening-the-reliability-and-security-of-the-united-states-electric-grid","status":"issued"},
  {"executive_order_number":14263,"title":"Addressing Risks From Susman Godfrey","html_url":"https://www.federalregister.gov/documents/2025/04/15/2025-06458/addressing-risks-from-susman-godfrey","status":"issued"},
  {"executive_order_number":14264,"title":"Maintaining Acceptable Water Pressure in Showerheads","html_url":"https://www.federalregister.gov/documents/2025/04/15/2025-06459/maintaining-acceptable-water-pressure-in-showerheads","status":"issued"},
  {"executive_order_number":14265,"title":"Modernizing Defense Acquisitions and Spurring Innovation in the Defense Industrial Base","html_url":"https://www.federalregister.gov/documents/2025/04/15/2025-06461/modernizing-defense-acquisitions-and-spurring-innovation-in-the-defense-industrial-base","status":"issued"},
  {"executive_order_number":14266,"title":"Modifying Reciprocal Tariff Rates To Reflect Trading Partner Retaliation and Alignment","html_url":"https://www.federalregister.gov/documents/2025/04/15/2025-06462/modifying-reciprocal-tariff-rates-to-reflect-trading-partner-retaliation-and-alignment","status":"issued"},
  {"executive_order_number":14267,"title":"Reducing Anti-Competitive Regulatory Barriers","html_url":"https://www.federalregister.gov/documents/2025/04/15/2025-06463/reducing-anti-competitive-regulatory-barriers","status":"issued"},
  {"executive_order_number":14268,"title":"Reforming Foreign Defense Sales To Improve Speed and Accountability","html_url":"https://www.federalregister.gov/documents/2025/04/15/2025-06464/reforming-foreign-defense-sales-to-improve-speed-and-accountability","status":"issued"},
  {"executive_order_number":14269,"title":"Restoring America's Maritime Dominance","html_url":"https://www.federalregister.gov/documents/2025/04/15/2025-06465/restoring-americas-maritime-dominance","status":"issued"},
  {"executive_order_number":14270,"title":"Zero-Based Regulatory Budgeting To Unleash American Energy","html_url":"https://www.federalregister.gov/documents/2025/04/15/2025-06466/zero-based-regulatory-budgeting-to-unleash-american-energy","status":"issued"},
  {"executive_order_number":14271,"title":"Ensuring Commercial, Cost-Effective Solutions in Federal Contracts","html_url":"https://www.federalregister.gov/documents/2025/04/18/2025-06835/ensuring-commercial-cost-effective-solutions-in-federal-contracts","status":"issued"},
  {"executive_order_number":14272,"title":"Ensuring National Security and Economic Resilience Through Section 232 Actions on Processed Critical Minerals and Derivative Products","html_url":"https://www.federalregister.gov/documents/2025/04/18/2025-06836/ensuring-national-security-and-economic-resilience-through-section-232-actions-on-processed-critical","status":"issued"},
  {"executive_order_number":14273,"title":"Lowering Drug Prices by Once Again Putting Americans First","html_url":"https://www.federalregister.gov/documents/2025/04/18/2025-06837/lowering-drug-prices-by-once-again-putting-americans-first","status":"issued"},
  {"executive_order_number":14274,"title":"Restoring Common Sense to Federal Office Space Management","html_url":"https://www.federalregister.gov/documents/2025/04/18/2025-06838/restoring-common-sense-to-federal-office-space-management","status":"issued"},
  {"executive_order_number":14275,"title":"Restoring Common Sense to Federal Procurement","html_url":"https://www.federalregister.gov/documents/2025/04/18/2025-06839/restoring-common-sense-to-federal-procurement","status":"issued"},
  {"executive_order_number":14276,"title":"Restoring American Seafood Competitiveness","html_url":"https://www.federalregister.gov/documents/2025/04/22/2025-07062/restoring-american-seafood-competitiveness","status":"issued"},
  {"executive_order_number":14277,"title":"Advancing Artificial Intelligence Education for American Youth","html_url":"https://www.federalregister.gov/documents/2025/04/28/2025-07368/advancing-artificial-intelligence-education-for-american-youth","status":"issued"},
  {"executive_order_number":14278,"title":"Preparing Americans for High-Paying Skilled Trade Jobs of the Future","html_url":"https://www.federalregister.gov/documents/2025/04/28/2025-07369/preparing-americans-for-high-paying-skilled-trade-jobs-of-the-future","status":"issued"},
  {"executive_order_number":14279,"title":"Reforming Accreditation To Strengthen Higher Education","html_url":"https://www.federalregister.gov/documents/2025/04/28/2025-07376/reforming-accreditation-to-strengthen-higher-education","status":"issued"},
  {"executive_order_number":14280,"title":"Reinstating Commonsense School Discipline Policies","html_url":"https://www.federalregister.gov/documents/2025/04/28/2025-07377/reinstating-commonsense-school-discipline-policies","status":"issued"},
  {"executive_order_number":14281,"title":"Restoring Equality of Opportunity and Meritocracy","html_url":"https://www.federalregister.gov/documents/2025/04/28/2025-07378/restoring-equality-of-opportunity-and-meritocracy","status":"issued"},
  {"executive_order_number":14282,"title":"Transparency Regarding Foreign Influence at American Universities","html_url":"https://www.federalregister.gov/documents/2025/04/28/2025-07379/transparency-regarding-foreign-influence-at-american-universities","status":"issued"},
  {"executive_order_number":14283,"title":"White House Initiative To Promote Excellence and Innovation at Historically Black Colleges and Universities","html_url":"https://www.federalregister.gov/documents/2025/04/28/2025-07380/white-house-initiative-to-promote-excellence-and-innovation-at-historically-black-colleges-and","status":"issued"},
  {"executive_order_number":14284,"title":"Strengthening Probationary Periods in the Federal Service","html_url":"https://www.federalregister.gov/documents/2025/04/29/2025-07469/strengthening-probationary-periods-in-the-federal-service","status":"issued"},
  {"executive_order_number":14285,"title":"Unleashing America's Offshore Critical Minerals and Resources","html_url":"https://www.federalregister.gov/documents/2025/04/29/2025-07470/unleashing-americas-offshore-critical-minerals-and-resources","status":"issued"},
  {"executive_order_number":14286,"title":"Enforcing Commonsense Rules of the Road for America's Truck Drivers","html_url":"https://www.federalregister.gov/documents/2025/05/02/2025-07786/enforcing-commonsense-rules-of-the-road-for-americas-truck-drivers","status":"issued"},
  {"executive_order_number":14287,"title":"Protecting American Communities From Criminal Aliens","html_url":"https://www.federalregister.gov/documents/2025/05/02/2025-07789/protecting-american-communities-from-criminal-aliens","status":"issued"},
  {"executive_order_number":14288,"title":"Strengthening and Unleashing America's Law Enforcement To Pursue Criminals and Protect Innocent Citizens","html_url":"https://www.federalregister.gov/documents/2025/05/02/2025-07790/strengthening-and-unleashing-americas-law-enforcement-to-pursue-criminals-and-protect-innocent","status":"issued"},
  {"executive_order_number":14289,"title":"Addressing Certain Tariffs on Imported Articles","html_url":"https://www.federalregister.gov/documents/2025/05/02/2025-07835/addressing-certain-tariffs-on-imported-articles","status":"issued"},
  {"executive_order_number":14290,"title":"Ending Taxpayer Subsidization of Biased Media","html_url":"https://www.federalregister.gov/documents/2025/05/07/2025-08133/ending-taxpayer-subsidization-of-biased-media","status":"issued"},
  {"executive_order_number":14291,"title":"Establishment of the Religious Liberty Commission","html_url":"https://www.federalregister.gov/documents/2025/05/07/2025-08134/establishment-of-the-religious-liberty-commission","status":"issued"},
  {"executive_order_number":14292,"title":"Improving the Safety and Security of Biological Research","html_url":"https://www.federalregister.gov/documents/2025/05/08/2025-08266/improving-the-safety-and-security-of-biological-research","status":"issued"},
  {"executive_order_number":14293,"title":"Regulatory Relief To Promote Domestic Production of Critical Medicines","html_url":"https://www.federalregister.gov/documents/2025/05/08/2025-08267/regulatory-relief-to-promote-domestic-production-of-critical-medicines","status":"issued"}
]

FILES = ["Feb28_2025.mp4","Feb28_2025.json","Feb28_2025.srt","Feb28_2025.tsv","Feb28_2025.txt","Feb28_2025.vtt","fighters.py","idea.py","openai_story.js","openai_story.py","TrumpChinaVirus2020.mp4","documents_signed_in_2025_signed_by_donald_trump_of_type_presidential_document_and_of_presidential_document_type_executive_order.csv","documents.json","apple-careers-us-accommodation-drugfree.pdf","Apple_Recruiting_Privacy_Policy.m4a","J50.mp4","TrumpModi.mp4","Donald_Hegseth_F47th_President.mp4"]

COLOR_MAP = {"issued":"#FFD700","pending":"yellow","blocked":"green","paused":"orange"}

TODAY = datetime.utcnow().date()
START_YEAR = 2025
RECENT_CUT = TODAY - timedelta(days=90)

BRANCH_RECRUIT = {"1":("Army","https://www.goarmy.com"),"2":("Marine Corps","https://www.marines.com"),"3":("Air Force","https://www.airforce.com"),"4":("Navy","https://www.navy.com"),"5":("Coast Guard","https://www.gocoastguard.com"),"6":("Space Force","https://www.airforce.com")}
RANK_INFO = {"1":("Private (E-1)","private_army.png","Army Private Insignia"),"2":("Private (E-1)","private_marine.png","Marine Private Insignia"),"3":("Airman Basic (E-1)","airman_basic.png","Airman Basic Insignia"),"4":("Seaman Recruit (E-1)","seaman_recruit.png","Navy Seaman Recruit Insignia"),"5":("Seaman Recruit (E-1)","seaman_recruit_cg.png","Coast Guard Seaman Recruit Insignia"),"6":("Specialist 1 (E-1)","specialist1_sf.png","Space Force Specialist 1 Insignia")}

def load_reference_json(path=REF_JSON):
    try:
        with open(path,"r",encoding="utf-8") as f:
            content = json.load(f)
    except FileNotFoundError:
        return []
    ref = content.get("results", content)
    out = []
    for r in ref:
        num = r.get("executive_order_number") or r.get("eo_number")
        if not num:
            continue
        try:
            num_int = int(num)
        except:
            continue
        out.append({
            "eo_number": num_int,
            "title": r.get("title","").strip(),
            "issue_date": r.get("signing_date","")[:10],
            "status": r.get("status","issued"),
            "rejection_date": r.get("rejection_date"),
            "link": r.get("html_url"),
            "rejection_link": r.get("rejection_link")
        })
    return out

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS eos(eo_number INTEGER PRIMARY KEY,title TEXT,issue_date TEXT,status TEXT,rejection_date TEXT,link TEXT,rejection_link TEXT)""")
    for d in DATA + load_reference_json():
        num = d.get("eo_number") or d.get("executive_order_number")
        if not num:
            continue
        issue_date = d.get("issue_date")
        if not issue_date and d.get("html_url"):
            parts = d["html_url"].split("/")
            if len(parts) > 6:
                issue_date = f"{parts[4]}-{parts[5]}-{parts[6]}"
        c.execute("""INSERT INTO eos(eo_number,title,issue_date,status,rejection_date,link,rejection_link) VALUES(?,?,?,?,?,?,?) ON CONFLICT(eo_number) DO UPDATE SET title=excluded.title,issue_date=excluded.issue_date,status=excluded.status,rejection_date=COALESCE(excluded.rejection_date,eos.rejection_date),link=COALESCE(excluded.link,eos.link),rejection_link=COALESCE(excluded.rejection_link,eos.rejection_link)""",
            (num,d.get("title",""),issue_date or "",d.get("status","issued"),d.get("rejection_date"),d.get("link") or d.get("html_url"),d.get("rejection_link")))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM eos", conn)
    conn.close()
    df["issue_date"] = pd.to_datetime(df["issue_date"],errors="coerce")
    df["rejection_date"] = pd.to_datetime(df["rejection_date"],errors="coerce")
    def eo_status(row):
        if pd.notna(row["rejection_date"]):
            link_low = (row["rejection_link"] or "").lower()
            if any(k in link_low for k in ("temporarily","preliminary","halts","injunction")):
                return "paused"
            return "blocked"
        if pd.isna(row["issue_date"]):
            return "issued"
        if row["issue_date"].date() >= RECENT_CUT:
            return "pending"
        return "issued"
    df["status"] = df.apply(eo_status, axis=1)
    df["display_date"] = np.where(df["status"].isin(["paused","blocked"]),df["rejection_date"],pd.Timestamp(TODAY))
    return df.sort_values("issue_date")

def make_figure(df):
    if df.empty:
        return "<p>No data available.</p>"
    counts = df["status"].value_counts().reindex(["issued","pending","paused","blocked"], fill_value=0)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=0.15, row_heights=[0.7,0.3])
    for _, r in df.iterrows():
        start, end = r["issue_date"], r["display_date"] if pd.notna(r["display_date"]) else pd.Timestamp(TODAY)
        link = r["link"] or "N/A"
        hover_txt = f"EO {r['eo_number']}: {r['title']}<br>Link: %{{customdata}}<extra></extra>"
        fig.add_trace(go.Scatter(x=[start,end],y=[r["eo_number"],r["eo_number"]],mode="lines",line=dict(color="#FFD700",width=4),customdata=[link,link],hovertemplate=hover_txt,showlegend=False),row=1,col=1)
        marker_args = dict(customdata=[link],hovertemplate=hover_txt,showlegend=False)
        if r["status"]=="blocked":
            fig.add_trace(go.Scatter(x=[r["rejection_date"]],y=[r["eo_number"]],mode="markers",marker=dict(color="green",symbol="x",size=9,line=dict(width=1,color="black")),**marker_args),row=1,col=1)
        elif r["status"]=="paused":
            fig.add_trace(go.Scatter(x=[r["rejection_date"]],y=[r["eo_number"]],mode="markers",marker=dict(color="orange",symbol="triangle-down",size=10,line=dict(width=1,color="black")),**marker_args),row=1,col=1)
        elif r["status"]=="pending":
            fig.add_trace(go.Scatter(x=[r["issue_date"]],y=[r["eo_number"]],mode="markers",marker=dict(color="yellow",symbol="triangle-up",size=9,line=dict(width=1,color="black")),**marker_args),row=1,col=1)
    fig.add_trace(go.Bar(x=list(counts.index),y=counts.values,marker_color=[COLOR_MAP[s] for s in counts.index],text=counts.values,textposition="auto"),row=2,col=1)
    fig.update_layout(title="GOP Executive Orders – America Is Back!",xaxis_title="Date",yaxis_title="EO Number",xaxis2_title="Status",yaxis2_title="Count",template="plotly_white",height=750,showlegend=False)
    return fig.to_html(full_html=False, include_plotlyjs="cdn")

init_db()
app = Flask(__name__)

def award_insignia(grade):
    dir_map={"E-1":"E1","E-2":"E2","E-3":"E3"}
    d=dir_map.get(grade)
    if not d: return ""
    folder=os.path.join(app.static_folder,d)
    if not os.path.isdir(folder): return ""
    images=[f for f in os.listdir(folder) if f.lower().endswith((".png",".jpg",".jpeg",".gif",".webp"))]
    if not images: return ""
    img=random.choice(images)
    src=f"/static/{d}/{img}"
    return f'''<div class="rank-msg">🎖️ Congratulations! You are now {grade}! Here's a random insignia:<br><a href="{src}" download><img src="{src}" alt="Mock {grade} Insignia" class="insignia"></a><br><small>Click the insignia to download.</small></div>'''


@app.route("/")
def index():
    branch = request.args.get("branch", "")
    grade = request.args.get("grade", "")
    complete = request.args.get("complete", "")
    branch_name, recruit_url = BRANCH_RECRUIT.get(branch, (None, None))

    df = load_data()
    graph_html = make_figure(df)
    graph_html += '''<div style="margin-top:8px;"><a href="https://americaisback.info/ero">americaisback.info/ero</a> | <a href="https://whitehouse.gov">whitehouse.gov</a></div><div style="font-size:2rem;line-height:1.4;">🤔🐼</div><div style="margin-top:4px;max-width:720px;">If Boeing could have allegedly patched some of the faulty MCAS system in the 737&nbsp;Max to a less faulty but still dangerous one per FAA, then anyone who thinks a little could do far better and perhaps concretely prove that the safety risk would be entirely fixed. Should Boeing pay a lot of money for this implementation solution that's provable to the government authorities that allow the 737&nbsp;Max to fly? So if Bo&nbsp;Shang accomplishes this in a day or less, is Trump Force&nbsp;One available for charter to Vladivostok?</div><div style="margin-top:8px;"><img src="/static/escorted_out.webp" alt="escorted_out" style="max-width:100%;height:auto;"></div><div style="color:red;font-weight:bold;margin-top:4px;max-width:720px;">SEVERE DIRE WARNING: The F-47 drones cannot fly as fast as Mr Pilot in the F-47, rendering them fucking worthless in every single possible scenario versus competing 6th-generation platforms such as the Chinese J-50. Did fucking Pete Hegseth dream about a swarm of AI drones? AI drones that take off far earlier than Mr Pilot to meet Mr Pilot there require a separate Mr Pilot flying a fat oil tanker to refuel in air for anything Pete's little head could daydream about.</div>'''

    issued_df = df[df["status"] == "issued"].sort_values("issue_date").copy()
    issued_df["date"] = issued_df["issue_date"].dt.strftime("%B %d, %Y")
    issued_list = issued_df[["eo_number", "title", "date"]].to_dict("records")

    blocked_df = df[df["status"] == "blocked"].sort_values("rejection_date").copy()
    blocked_df["date"] = blocked_df["rejection_date"].dt.strftime("%B %d, %Y")

    paused_df = df[df["status"] == "paused"].sort_values("rejection_date").copy()
    paused_df["date"] = paused_df["rejection_date"].dt.strftime("%B %d, %Y")

    not_active = pd.concat([blocked_df, paused_df], ignore_index=True).sort_values("rejection_date")
    not_active_list = not_active[["eo_number", "title", "date", "status"]].to_dict("records")

    issued_count = len(issued_list)
    blocked_count = len(blocked_df)
    paused_count = len(paused_df)

    files_info = [
        {"name": f, "exists": os.path.isfile(os.path.join(app.static_folder, f))}
        for f in FILES
    ]

    grade_form_html = training_button_html = award_html = rank_msg_html = ""

    if branch and not (grade and complete):
        rank_msg_html = '<div class="rank-msg">🎂 In Basic Training, you don\'t have a rank yet 🎂</div>'
    if branch and not grade:
        grade_form_html = f"""
<form method="get" style='margin-top:16px;'>
  <input type="hidden" name="branch" value="{branch}">
  <label for="grade" style="font-size:1.25rem;margin-right:12px;color:#fff;">Select your starting grade</label>
  <select name="grade" id="grade" class="branch-select" required>
    <option value="" disabled selected>--</option>
    <option value="E-1">E-1</option>
    <option value="E-2">E-2</option>
    <option value="E-3">E-3</option>
  </select>
  <button type="submit">Select</button>
</form>"""
    elif branch and grade and not complete:
        training_button_html = f"""
<form method="get" style='margin-top:16px;'>
  <input type="hidden" name="branch" value="{branch}">
  <input type="hidden" name="grade" value="{grade}">
  <input type="hidden" name="complete" value="1">
  <button type="submit">🚌💨 Complete Basic Training</button>
</form>"""
    elif branch and grade and complete:
        award_html = award_insignia(grade)

    return render_template_string(
        open("template.html", "r", encoding="utf-8").read(),
        branch=branch,
        branch_name=branch_name,
        recruit_url=recruit_url,
        graph=graph_html,
        yr_range=f"{START_YEAR}-{TODAY.year}" if TODAY.year > START_YEAR else str(TODAY.year),
        issued_count=issued_count,
        blocked_count=blocked_count,
        paused_count=paused_count,
        issued=issued_list,
        not_active=not_active_list,
        files=files_info,
        grade_form=grade_form_html,
        training_button=training_button_html,
        award=award_html,
        rank_msg=rank_msg_html,
        TODAY=TODAY,
        START_YEAR=START_YEAR
    )

@app.route("/data.csv")
def data_csv():
    df=load_data()
    return Response(df.to_csv(index=False),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=gop_trump_eos.csv"})

@app.route("/data.json")
def data_json():
    df=load_data()
    return Response(df.to_json(orient="records", date_format="iso"),mimetype="application/json")

@app.route("/download/<path:filename>")
def download_file(filename):
    file_path=os.path.join(app.static_folder,filename)
    if not os.path.isfile(file_path):
        return Response(f"Error: {filename} not found.", status=404, mimetype="text/plain")
    return send_from_directory(app.static_folder,filename,as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=4999, debug=False)