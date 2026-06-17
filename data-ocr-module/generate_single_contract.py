"""Generate a single realistic 10-15 page contract PDF for quick upload testing."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os

CONTRACT_TEXT = """
MASTER SERVICES AGREEMENT

This Master Services Agreement ("Agreement") is entered into as of March 15, 2025 ("Effective Date"), by and between:

SERVICE PROVIDER: Nextera Technologies Inc., a corporation organized and existing under the laws of the State of Delaware, with its principal offices located at 245 Park Avenue, 36th Floor, New York, NY 10167, United States, Tax ID: 84-2938475, represented by James Harrington III, Chief Executive Officer, email: james.harrington@nextera.com, phone: (212) 555-8901 ("Provider" or "Nextera");

AND

CLIENT: Atlas Global Solutions LLC, a limited liability company organized and existing under the laws of the State of California, with its principal offices located at 1 Market Street, Suite 3600, San Francisco, CA 94105, United States, Tax ID: 91-7463829, represented by Sarah Chen-Williams, Chief Operating Officer, email: sarah.chen@atlasglobal.com, phone: (415) 555-3472 ("Client" or "Atlas").

The Provider and the Client are individually referred to as a "Party" and collectively as the "Parties."

RECITALS

WHEREAS, the Provider is a technology company specializing in enterprise software development, cloud computing solutions, artificial intelligence and machine learning services, data analytics platforms, and digital transformation consulting;

WHEREAS, the Client is a multinational organization with operations spanning North America, Europe, and Asia-Pacific, seeking to modernize its technology infrastructure and implement advanced digital solutions across its global operations;

WHEREAS, the Client desires to engage the Provider to deliver comprehensive technology services, including but not limited to custom software development, cloud migration, AI/ML implementation, data analytics deployment, cybersecurity enhancement, and ongoing managed services;

WHEREAS, the Provider has the technical expertise, qualified personnel, and operational capabilities to deliver the services requested by the Client;

WHEREAS, the Parties have conducted extensive due diligence, including technical assessments, reference checks, security audits, and financial reviews, and have determined that a business relationship would be mutually beneficial;

NOW, THEREFORE, in consideration of the mutual covenants, promises, and agreements contained herein, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties agree as follows:


ARTICLE 1 - DEFINITIONS

1.1 "Acceptance" means the Client's written confirmation that a Deliverable meets the Acceptance Criteria specified in the applicable Statement of Work.

1.2 "Acceptance Criteria" means the functional, technical, and performance requirements that a Deliverable must satisfy, as specified in the applicable Statement of Work.

1.3 "Affiliate" means any entity that directly or indirectly controls, is controlled by, or is under common control with a Party, where "control" means the ownership of more than fifty percent (50%) of the voting securities or equivalent ownership interest.

1.4 "Authorized Users" means the Client's employees, contractors, agents, and Affiliates who are authorized to access and use the Deliverables pursuant to this Agreement. The initial number of Authorized Users shall be 2,500, with the option to increase to 10,000 users upon written notice.

1.5 "Business Day" means any day other than a Saturday, Sunday, or public holiday in the State of New York or the State of California.

1.6 "Change Order" means a written document executed by both Parties that modifies the scope, schedule, or fees of a Statement of Work.

1.7 "Confidential Information" means all non-public information disclosed by one Party to the other, whether orally, in writing, electronically, or by inspection, including but not limited to: trade secrets, proprietary technology, source code, algorithms, business plans, financial data, customer lists, marketing strategies, pricing information, employee data, product roadmaps, technical specifications, and any information marked as "Confidential," "Proprietary," or with a similar designation.

1.8 "Deliverables" means all work product, software, documentation, reports, designs, specifications, code, data, and other materials created by the Provider in the performance of Services under this Agreement.

1.9 "Force Majeure Event" means any event beyond the reasonable control of the affected Party, including acts of God, war, terrorism, civil unrest, epidemics, pandemics (including COVID-19 and any variants), government orders or regulations, natural disasters, fire, flood, earthquake, hurricane, tornado, volcanic eruption, power failures, telecommunications failures, Internet outages, cyberattacks (excluding those resulting from the affected Party's failure to maintain reasonable security measures), labor strikes, and supply chain disruptions.

1.10 "Intellectual Property Rights" means all patents, copyrights, trademarks, trade secrets, moral rights, rights of publicity, and all other intellectual property rights recognized in any jurisdiction worldwide, whether registered or unregistered, and including all applications and registrations relating thereto.

1.11 "Personal Data" means any information that identifies, relates to, describes, or could reasonably be linked to a natural person, as defined by applicable data protection laws including the General Data Protection Regulation (GDPR), the California Consumer Privacy Act (CCPA), the California Privacy Rights Act (CPRA), and other applicable privacy regulations.

1.12 "Services" means the professional services, consulting, software development, implementation, training, support, and maintenance services to be provided by the Provider as described in one or more Statements of Work.

1.13 "Statement of Work" or "SOW" means a written document, substantially in the form attached hereto as Exhibit A, that describes the specific Services to be performed, Deliverables to be produced, timelines, milestones, and fees.


ARTICLE 2 - SCOPE OF SERVICES

2.1 Engagement. The Client hereby engages the Provider, and the Provider hereby agrees, to perform the Services described in this Agreement and in each Statement of Work executed by the Parties from time to time.

2.2 Statements of Work. Each Statement of Work shall include, at a minimum: (a) a detailed description of the Services to be performed; (b) specific Deliverables; (c) Acceptance Criteria for each Deliverable; (d) timeline and milestones; (e) fees and payment schedule; (f) key personnel assignments; (g) assumptions and dependencies; and (h) any special terms or conditions applicable to that engagement.

2.3 Initial Engagement. The initial engagement under this Agreement shall consist of the following workstreams:
  (a) Enterprise Cloud Migration - Migration of Client's on-premises infrastructure to AWS and Azure cloud platforms, including 47 applications, 12 databases, and 8 data warehouses;
  (b) AI/ML Platform Development - Design and deployment of a custom machine learning platform for predictive analytics, natural language processing, and computer vision applications;
  (c) Cybersecurity Enhancement - Implementation of zero-trust architecture, security information and event management (SIEM), and penetration testing across all environments;
  (d) Data Analytics Dashboard - Development of executive dashboards and self-service analytics tools using real-time data integration from 15+ data sources;
  (e) Legacy System Modernization - Refactoring and modernization of 12 legacy applications using microservices architecture and containerization.

2.4 Standards of Performance. The Provider shall perform all Services: (a) in a professional, competent, and workmanlike manner; (b) in accordance with industry best practices and applicable professional standards; (c) using qualified personnel with relevant experience and expertise; (d) in compliance with all applicable laws, regulations, and ordinances; and (e) in accordance with the timelines and specifications set forth in the applicable Statement of Work.

2.5 Key Personnel. The Provider shall assign the following key personnel to the engagement: (a) Robert J. Fitzgerald, Program Director; (b) Dr. Priya Sharma, Chief Architect; (c) Michael K. Tanaka, Security Lead; (d) Amanda Leigh Patterson, Data Science Lead. Key personnel shall not be reassigned or replaced without the prior written consent of the Client, which shall not be unreasonably withheld.

2.6 Subcontractors. The Provider may engage subcontractors to perform portions of the Services, provided that: (a) the Provider obtains the Client's prior written consent; (b) the subcontractor is bound by confidentiality and security obligations no less restrictive than those in this Agreement; (c) the Provider remains fully responsible for the subcontractor's performance; and (d) the Provider ensures that the subcontractor complies with all applicable laws and regulations.


ARTICLE 3 - COMPENSATION AND PAYMENT

3.1 Total Contract Value. The total compensation payable under this Agreement for the initial engagement shall not exceed Twelve Million Five Hundred Thousand United States Dollars ($12,500,000.00) (the "Total Contract Value"), inclusive of all professional fees, travel expenses, and applicable taxes.

3.2 Fee Structure. The Services shall be billed according to the following rate card:
  (a) Program Director: $425.00 per hour
  (b) Solution Architect: $375.00 per hour
  (c) Senior Developer: $325.00 per hour
  (d) Developer: $275.00 per hour
  (e) QA Engineer: $225.00 per hour
  (f) Project Manager: $300.00 per hour
  (g) Data Scientist: $350.00 per hour
  (h) Security Engineer: $350.00 per hour
  (i) DevOps Engineer: $300.00 per hour
  (j) Business Analyst: $250.00 per hour

3.3 Payment Schedule. The Client shall pay the Provider according to the following schedule:
  (a) Upon execution of this Agreement: $1,875,000.00 (15% mobilization payment);
  (b) Monthly progress payments based on verified time and materials, due within thirty (30) days of invoice receipt;
  (c) Milestone payments as specified in each Statement of Work;
  (d) Ten percent (10%) retention on each invoice, to be released upon Acceptance of the final Deliverable.

3.4 Invoicing. The Provider shall submit detailed invoices on a monthly basis, no later than the tenth (10th) Business Day of each calendar month for Services performed in the preceding month. Each invoice shall include: (a) itemized description of Services performed; (b) hours worked by each team member; (c) hourly rates applied; (d) travel and expense reimbursements with receipts; (e) milestone completion status; (f) applicable taxes; and (g) cumulative total billed to date versus Total Contract Value.

3.5 Payment Terms. The Client shall pay all undisputed amounts within thirty (30) days of receipt of a conforming invoice. Late payments shall accrue interest at the rate of one and one-half percent (1.5%) per month, or the maximum rate permitted by applicable law, whichever is less, calculated from the due date until the date of payment.

3.6 Disputed Invoices. If the Client disputes any portion of an invoice, the Client shall: (a) pay the undisputed portion by the due date; (b) provide written notice of the dispute with specific details within fifteen (15) days of receipt; and (c) cooperate in good faith to resolve the dispute within thirty (30) days.

3.7 Expenses. The Provider shall be entitled to reimbursement for reasonable and pre-approved travel, lodging, and other out-of-pocket expenses incurred in connection with the Services, not to exceed $375,000.00 per year. All expenses shall be documented with receipts and shall comply with the Client's travel and expense policy.

3.8 Taxes. All fees are exclusive of applicable taxes. The Client shall be responsible for all sales, use, value-added, and similar taxes, except for taxes based on the Provider's net income. The Provider shall provide tax invoices as required by applicable law.

3.9 Annual Rate Adjustment. The hourly rates set forth in Section 3.2 may be adjusted annually on each anniversary of the Effective Date by an amount not to exceed the greater of: (a) three percent (3%); or (b) the Consumer Price Index (CPI) increase for the preceding twelve (12) month period, with sixty (60) days' prior written notice.


ARTICLE 4 - TERM AND TERMINATION

4.1 Term. This Agreement shall commence on the Effective Date and continue for an initial term of three (3) years (the "Initial Term"), unless earlier terminated in accordance with this Article.

4.2 Renewal. This Agreement may be renewed for additional one-year periods (each a "Renewal Term") upon mutual written agreement of the Parties, executed at least ninety (90) days prior to the expiration of the then-current term. The Initial Term and any Renewal Terms are collectively referred to as the "Term."

4.3 Termination for Convenience. Either Party may terminate this Agreement for convenience upon ninety (90) days' prior written notice to the other Party. In the event of termination for convenience by the Client, the Client shall pay the Provider for: (a) all Services performed and expenses incurred through the date of termination; (b) any non-cancellable commitments made by the Provider on behalf of the Client; and (c) a wind-down fee equal to two (2) months of the average monthly billing for the preceding six (6) months.

4.4 Termination for Cause. Either Party may terminate this Agreement immediately upon written notice if: (a) the other Party commits a material breach and fails to cure such breach within thirty (30) days after receipt of written notice specifying the breach in reasonable detail; (b) the other Party becomes insolvent, files for bankruptcy or reorganization under any applicable bankruptcy law, has a receiver appointed for substantially all of its assets, or makes an assignment for the benefit of creditors; (c) the other Party is convicted of fraud, bribery, or other criminal misconduct related to the performance of this Agreement; or (d) the other Party fails to maintain the insurance coverage required by this Agreement for a period exceeding fifteen (15) days.

4.5 Termination for Regulatory Reasons. Either Party may terminate this Agreement upon thirty (30) days' written notice if performance of the Agreement would cause either Party to violate any applicable law, regulation, or government order.

4.6 Effect of Termination. Upon termination or expiration of this Agreement: (a) all rights granted hereunder shall immediately cease, except as expressly stated herein; (b) the Provider shall promptly deliver to the Client all completed and in-progress Deliverables, work product, documentation, and Client data; (c) the Provider shall cooperate with the Client in transitioning Services to the Client or a successor provider for a period of up to six (6) months (the "Transition Period"); (d) the Client shall pay for all Services performed through the date of termination and during the Transition Period; and (e) all provisions that by their nature should survive termination shall survive, including confidentiality, intellectual property, indemnification, limitation of liability, and governing law.


ARTICLE 5 - CONFIDENTIALITY

5.1 Obligations. Each Party (the "Receiving Party") shall: (a) hold the other Party's (the "Disclosing Party's") Confidential Information in strict confidence; (b) not disclose such Confidential Information to any third party without the prior written consent of the Disclosing Party; (c) use such Confidential Information only for the purposes of performing its obligations under this Agreement; (d) limit access to Confidential Information to those employees, agents, and advisors who have a need to know and who are bound by confidentiality obligations no less restrictive than those contained herein; and (e) protect Confidential Information using at least the same degree of care it uses to protect its own most sensitive confidential information, but in no event less than reasonable care.

5.2 Exceptions. Confidential Information shall not include information that: (a) is or becomes publicly available through no fault of the Receiving Party; (b) was rightfully in the Receiving Party's possession prior to disclosure, as evidenced by written records; (c) is independently developed by the Receiving Party without use of or reference to the Disclosing Party's Confidential Information; (d) is rightfully obtained from a third party without restriction on disclosure; or (e) is required to be disclosed by law, regulation, or court order, provided that the Receiving Party gives the Disclosing Party prompt written notice and cooperates in seeking a protective order.

5.3 Return of Materials. Upon termination of this Agreement or upon written request by the Disclosing Party, the Receiving Party shall promptly return or destroy all copies of the Disclosing Party's Confidential Information and certify in writing that it has done so, except for copies retained in accordance with routine backup procedures or as required by applicable law.

5.4 Duration. The obligations of confidentiality shall survive the termination or expiration of this Agreement for a period of seven (7) years, provided that obligations relating to trade secrets shall continue for as long as such information remains a trade secret under applicable law.

5.5 Injunctive Relief. Each Party acknowledges that any unauthorized disclosure or use of Confidential Information may cause irreparable harm for which monetary damages would be inadequate. Accordingly, each Party shall be entitled to seek injunctive relief, specific performance, or other equitable remedies, in addition to any other remedies available at law or in equity, without the requirement of posting a bond or other security.


ARTICLE 6 - INTELLECTUAL PROPERTY

6.1 Client Ownership. All Deliverables and work product created by the Provider specifically for the Client under this Agreement ("Client IP") shall be the sole and exclusive property of the Client. The Provider hereby assigns, and agrees to assign, all right, title, and interest in and to the Client IP, including all Intellectual Property Rights therein, to the Client.

6.2 Provider Pre-Existing IP. The Provider retains all right, title, and interest in and to any pre-existing intellectual property, tools, frameworks, libraries, methodologies, and know-how that the Provider owned prior to the Effective Date or develops independently outside the scope of this Agreement ("Provider IP"). To the extent that any Provider IP is incorporated into the Deliverables, the Provider hereby grants to the Client a perpetual, irrevocable, non-exclusive, worldwide, fully paid-up, royalty-free license to use, modify, and create derivative works of such Provider IP solely in connection with the Client's use of the Deliverables.

6.3 Third-Party Components. The Provider shall obtain all necessary licenses for any third-party software, tools, or components incorporated into the Deliverables. The Provider shall disclose all third-party components to the Client prior to incorporation and shall ensure that the license terms are compatible with the Client's intended use.

6.4 Non-Infringement Warranty. The Provider represents and warrants that: (a) the Deliverables shall not infringe upon any third party's Intellectual Property Rights; (b) the Provider has the full right, power, and authority to enter into this Agreement and grant the rights contemplated herein; and (c) the Provider has not previously assigned, transferred, or encumbered the rights granted herein.


ARTICLE 7 - DATA PRIVACY AND SECURITY

7.1 Compliance. The Provider shall comply with all applicable data protection and privacy laws, including the General Data Protection Regulation (EU) 2016/679 ("GDPR"), the California Consumer Privacy Act ("CCPA"), the California Privacy Rights Act ("CPRA"), the Health Insurance Portability and Accountability Act ("HIPAA") where applicable, and all other applicable federal, state, and international data protection regulations.

7.2 Data Processing Agreement. The Parties shall enter into a Data Processing Agreement ("DPA") substantially in the form attached as Exhibit C, which shall govern the processing of Personal Data by the Provider on behalf of the Client. The DPA shall include: (a) categories of Personal Data processed; (b) purposes and duration of processing; (c) rights and obligations of each Party; (d) technical and organizational security measures; and (e) sub-processor management requirements.

7.3 Security Measures. The Provider shall implement and maintain comprehensive administrative, physical, and technical safeguards to protect Client data, including but not limited to: (a) AES-256 encryption for data at rest; (b) TLS 1.3 encryption for data in transit; (c) multi-factor authentication for all system access; (d) role-based access controls with least privilege principles; (e) continuous security monitoring and intrusion detection systems; (f) regular vulnerability assessments and penetration testing (at least quarterly); (g) security awareness training for all personnel with access to Client data; and (h) documented incident response procedures.

7.4 Data Breach Notification. In the event of a confirmed data breach involving Client data, the Provider shall: (a) notify the Client within twenty-four (24) hours of confirming the breach; (b) provide detailed information about the nature and scope of the breach; (c) take immediate steps to contain the breach and prevent further unauthorized access; (d) cooperate with the Client's investigation and remediation efforts; (e) provide regular updates until the breach is fully resolved; and (f) bear all reasonable costs associated with breach notification, credit monitoring, and remediation.

7.5 Data Location. All Client data shall be stored and processed within the continental United States, specifically in the Provider's SOC 2 Type II certified data centers located in Ashburn, Virginia (primary) and Portland, Oregon (disaster recovery). The Provider shall not transfer Client data outside the United States without the prior written consent of the Client.

7.6 Data Retention and Deletion. Upon termination of this Agreement, the Provider shall: (a) make all Client data available for export in a standard, machine-readable format for a period of ninety (90) days; (b) permanently delete all Client data from its systems, including backups, within thirty (30) days following the export period; and (c) certify in writing that all Client data has been securely destroyed.

7.7 Audit Rights. The Client shall have the right to audit the Provider's compliance with the data privacy and security requirements of this Agreement upon thirty (30) days' prior written notice. Audits shall be conducted during normal business hours, no more than once per calendar year, and at the Client's expense unless the audit reveals a material non-compliance, in which case the Provider shall bear the audit costs.


ARTICLE 8 - INDEMNIFICATION

8.1 Provider Indemnification. The Provider shall indemnify, defend, and hold harmless the Client, its Affiliates, and their respective officers, directors, employees, agents, successors, and assigns (the "Client Indemnified Parties") from and against any and all third-party claims, demands, suits, proceedings, losses, damages, liabilities, costs, and expenses (including reasonable attorneys' fees and court costs) (collectively, "Losses") arising out of or relating to: (a) any claim that the Deliverables or Services infringe any patent, copyright, trademark, trade secret, or other Intellectual Property Right of any third party; (b) any breach by the Provider of its representations, warranties, or obligations under this Agreement; (c) any negligent or willful acts or omissions of the Provider, its employees, agents, or subcontractors; (d) any breach of applicable data protection or privacy laws; (e) any personal injury or property damage caused by the Provider in the performance of the Services; or (f) any failure by the Provider to comply with applicable laws and regulations.

8.2 Client Indemnification. The Client shall indemnify, defend, and hold harmless the Provider, its Affiliates, and their respective officers, directors, employees, agents, successors, and assigns (the "Provider Indemnified Parties") from and against any Losses arising out of or relating to: (a) any breach by the Client of its representations, warranties, or obligations under this Agreement; (b) any negligent or willful acts or omissions of the Client, its employees, or agents; (c) any claim arising from the Client's use of the Deliverables in a manner not authorized by this Agreement; or (d) any materials, data, or content provided by the Client to the Provider that infringes any third-party rights.

8.3 Indemnification Procedures. The indemnified Party shall: (a) provide prompt written notice of any claim; (b) grant the indemnifying Party sole control of the defense and settlement; (c) provide reasonable cooperation and assistance; and (d) not settle or compromise any claim without the indemnifying Party's prior written consent. The indemnifying Party shall not settle any claim in a manner that imposes any obligation on the indemnified Party without the indemnified Party's prior written consent.


ARTICLE 9 - LIMITATION OF LIABILITY

9.1 Cap on Liability. THE TOTAL AGGREGATE LIABILITY OF EITHER PARTY UNDER THIS AGREEMENT, WHETHER IN CONTRACT, TORT (INCLUDING NEGLIGENCE), STRICT LIABILITY, OR OTHERWISE, SHALL NOT EXCEED THE GREATER OF: (A) THE TOTAL FEES ACTUALLY PAID OR PAYABLE BY THE CLIENT TO THE PROVIDER DURING THE TWELVE (12) MONTH PERIOD IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO THE CLAIM; OR (B) FIVE MILLION UNITED STATES DOLLARS ($5,000,000.00).

9.2 Exclusion of Consequential Damages. IN NO EVENT SHALL EITHER PARTY BE LIABLE TO THE OTHER PARTY FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, PUNITIVE, OR EXEMPLARY DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, LOSS OF REVENUE, LOSS OF DATA, LOSS OF BUSINESS OPPORTUNITIES, LOSS OF GOODWILL, BUSINESS INTERRUPTION, OR COST OF PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, REGARDLESS OF THE CAUSE OF ACTION OR THE THEORY OF LIABILITY, EVEN IF SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

9.3 Exceptions. THE LIMITATIONS SET FORTH IN SECTIONS 9.1 AND 9.2 SHALL NOT APPLY TO: (A) BREACHES OF ARTICLE 5 (CONFIDENTIALITY); (B) OBLIGATIONS UNDER ARTICLE 8 (INDEMNIFICATION); (C) WILLFUL MISCONDUCT, FRAUD, OR GROSS NEGLIGENCE; (D) BREACHES OF ARTICLE 7 (DATA PRIVACY AND SECURITY); OR (E) INFRINGEMENT OF INTELLECTUAL PROPERTY RIGHTS.

9.4 Essential Basis. THE PARTIES ACKNOWLEDGE THAT THE LIMITATIONS OF LIABILITY SET FORTH IN THIS ARTICLE REPRESENT THE ALLOCATION OF RISK BETWEEN THE PARTIES AND FORM AN ESSENTIAL BASIS OF THE BARGAIN BETWEEN THE PARTIES.


ARTICLE 10 - INSURANCE

10.1 Required Coverage. The Provider shall maintain, at its own expense, the following insurance coverage throughout the Term and for a period of two (2) years following termination:

  (a) Commercial General Liability: $5,000,000.00 per occurrence and $10,000,000.00 in the aggregate, covering bodily injury, property damage, and personal and advertising injury;

  (b) Professional Liability / Errors and Omissions: $10,000,000.00 per claim and $15,000,000.00 in the aggregate, covering acts, errors, and omissions in the performance of professional services;

  (c) Cyber Liability and Technology Errors and Omissions: $15,000,000.00 per claim and $20,000,000.00 in the aggregate, covering data breaches, privacy violations, network security failures, and technology professional services;

  (d) Workers' Compensation: as required by applicable law in all jurisdictions where the Provider's employees perform Services;

  (e) Employer's Liability: $2,000,000.00 per accident, $2,000,000.00 disease policy limit, and $2,000,000.00 disease each employee;

  (f) Commercial Automobile Liability: $2,000,000.00 combined single limit, covering owned, hired, and non-owned vehicles;

  (g) Umbrella / Excess Liability: $25,000,000.00 per occurrence and in the aggregate, in excess of the underlying Commercial General Liability, Automobile Liability, and Employer's Liability policies;

  (h) Crime / Fidelity Bond: $5,000,000.00 covering employee dishonesty, forgery, computer fraud, and funds transfer fraud.

10.2 Additional Insured. The Client shall be named as an additional insured on the Provider's Commercial General Liability, Automobile Liability, and Umbrella policies.

10.3 Certificates of Insurance. The Provider shall provide the Client with certificates of insurance evidencing the required coverage within ten (10) days of the Effective Date and upon each renewal thereafter. The Provider shall provide thirty (30) days' prior written notice to the Client of any material change, cancellation, or non-renewal of required coverage.


ARTICLE 11 - REPRESENTATIONS AND WARRANTIES

11.1 Mutual Representations. Each Party represents and warrants that: (a) it is duly organized, validly existing, and in good standing under the laws of its jurisdiction of organization; (b) it has the full right, power, and authority to enter into this Agreement and perform its obligations hereunder; (c) the execution and performance of this Agreement does not conflict with any other agreement to which it is a party; and (d) it shall comply with all applicable laws, regulations, and ordinances in the performance of its obligations.

11.2 Provider Warranties. The Provider additionally represents and warrants that: (a) the Services shall be performed in a professional and workmanlike manner by qualified personnel; (b) the Deliverables shall conform to the specifications and Acceptance Criteria in the applicable Statement of Work; (c) the Deliverables shall be free from material defects for a period of twelve (12) months following Acceptance ("Warranty Period"); (d) the Deliverables shall not contain any viruses, malware, trojan horses, backdoors, or other malicious code; (e) the Provider has not been debarred, suspended, or proposed for debarment by any government agency; and (f) no portion of the Services shall be performed using forced, compulsory, or child labor.


ARTICLE 12 - FORCE MAJEURE

12.1 Excuse from Performance. Neither Party shall be liable for any delay or failure to perform its obligations under this Agreement to the extent that such delay or failure is caused by a Force Majeure Event, provided that the affected Party: (a) gives the other Party prompt written notice of the Force Majeure Event, including a description of the event and an estimate of its duration; (b) uses commercially reasonable efforts to mitigate the effects of the Force Majeure Event; (c) continues to perform any obligations not affected by the Force Majeure Event; and (d) provides regular updates on the status and expected resolution.

12.2 Termination. If a Force Majeure Event continues for more than ninety (90) consecutive days, either Party may terminate this Agreement upon thirty (30) days' written notice without liability, except for payment obligations for Services already performed.


ARTICLE 13 - GOVERNING LAW AND DISPUTE RESOLUTION

13.1 Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the State of New York, without regard to its conflict of laws principles. The United Nations Convention on Contracts for the International Sale of Goods shall not apply to this Agreement.

13.2 Negotiation. The Parties shall first attempt to resolve any dispute arising out of or relating to this Agreement through good faith negotiation between senior executives of each Party. If the dispute cannot be resolved through negotiation within forty-five (45) days, either Party may proceed to arbitration as provided below.

13.3 Arbitration. Any dispute, controversy, or claim arising out of or relating to this Agreement, or the breach, termination, or invalidity thereof, shall be settled by binding arbitration administered by the American Arbitration Association ("AAA") in accordance with its Commercial Arbitration Rules and Supplementary Procedures for Large, Complex Commercial Disputes.

13.4 The arbitration shall be conducted by a panel of three (3) arbitrators, with each Party selecting one arbitrator and the two Party-selected arbitrators selecting the third. The arbitration shall take place in New York, New York, and shall be conducted in the English language.

13.5 The arbitrators' award shall be final and binding, and judgment upon the award may be entered in any court of competent jurisdiction. The prevailing Party shall be entitled to recover its reasonable attorneys' fees, costs, and expenses from the non-prevailing Party.


ARTICLE 14 - GENERAL PROVISIONS

14.1 Entire Agreement. This Agreement, together with all Exhibits, Statements of Work, and Change Orders, constitutes the entire agreement between the Parties with respect to the subject matter hereof and supersedes all prior and contemporaneous agreements, understandings, negotiations, and discussions, whether oral or written.

14.2 Amendment. This Agreement may only be amended, modified, or supplemented by a written instrument duly executed by authorized representatives of both Parties.

14.3 Assignment. Neither Party may assign this Agreement or any of its rights or obligations hereunder without the prior written consent of the other Party, except that either Party may assign this Agreement in connection with a merger, acquisition, corporate reorganization, or sale of all or substantially all of its assets, provided that the assignee agrees in writing to be bound by all terms and conditions of this Agreement.

14.4 Notices. All notices, requests, consents, and other communications required or permitted under this Agreement shall be in writing and shall be deemed given: (a) when delivered personally; (b) one (1) Business Day after being sent by recognized overnight courier; (c) three (3) Business Days after being sent by certified or registered mail, postage prepaid, return receipt requested; or (d) when sent by email with confirmation of receipt (excluding auto-replies).

If to Provider:
Nextera Technologies Inc.
Attn: Legal Department
245 Park Avenue, 36th Floor
New York, NY 10167
Email: legal@nextera.com
Phone: (212) 555-8901

If to Client:
Atlas Global Solutions LLC
Attn: Office of General Counsel
1 Market Street, Suite 3600
San Francisco, CA 94105
Email: legal@atlasglobal.com
Phone: (415) 555-3472

14.5 Severability. If any provision of this Agreement is held to be invalid, illegal, or unenforceable by a court of competent jurisdiction, the remaining provisions shall continue in full force and effect, and the Parties shall negotiate in good faith a replacement provision that most closely approximates the intent of the original provision.

14.6 Waiver. No waiver of any provision of this Agreement shall be effective unless in writing and signed by the waiving Party. No waiver shall constitute a continuing waiver or a waiver of any subsequent breach of the same or a different provision.

14.7 No Third-Party Beneficiaries. This Agreement is entered into solely between the Parties and does not create any rights in any third party.

14.8 Independent Contractor. The Provider is an independent contractor and not an employee, agent, joint venturer, or partner of the Client. Neither Party has the authority to bind the other or to incur any obligations on behalf of the other.

14.9 Counterparts. This Agreement may be executed in any number of counterparts, each of which shall be deemed an original and all of which together shall constitute one and the same instrument. Electronic signatures and PDF copies shall have the same legal effect as original signatures.

14.10 Survival. The following Articles shall survive the termination or expiration of this Agreement: Article 1 (Definitions), Article 5 (Confidentiality), Article 6 (Intellectual Property), Article 7 (Data Privacy and Security), Article 8 (Indemnification), Article 9 (Limitation of Liability), Article 13 (Governing Law and Dispute Resolution), and Article 14 (General Provisions).

14.11 Order of Precedence. In the event of a conflict between the terms of this Agreement and any Statement of Work, the terms of this Agreement shall prevail unless the Statement of Work expressly states that it is intended to supersede a specific provision of this Agreement.


IN WITNESS WHEREOF, the Parties have caused this Agreement to be executed by their duly authorized representatives as of the Effective Date first written above.


SERVICE PROVIDER: Nextera Technologies Inc.

By: ____________________________
Name: James Harrington III
Title: Chief Executive Officer
Date: March 15, 2025


CLIENT: Atlas Global Solutions LLC

By: ____________________________
Name: Sarah Chen-Williams
Title: Chief Operating Officer
Date: March 15, 2025


WITNESS:

By: ____________________________
Name: Robert J. Fitzgerald
Title: Program Director, Nextera Technologies Inc.
Date: March 15, 2025

By: ____________________________
Name: Dr. Priya Sharma
Title: Chief Architect, Nextera Technologies Inc.
Date: March 15, 2025
"""

def build():
    output = os.path.join(os.path.dirname(__file__), "Test_Contract_MSA.pdf")
    
    doc = SimpleDocTemplate(
        output, pagesize=letter,
        leftMargin=1*inch, rightMargin=1*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
    )
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Title2", parent=styles["Heading1"], fontSize=18, spaceAfter=20, alignment=TA_CENTER, textColor=colors.HexColor("#0f3460")))
    styles.add(ParagraphStyle("Body2", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=8))
    styles.add(ParagraphStyle("Section2", parent=styles["Heading2"], fontSize=12, spaceBefore=16, spaceAfter=8, textColor=colors.HexColor("#16213e")))
    
    elements = []
    
    # Cover
    elements.append(Spacer(1, 2.5*inch))
    elements.append(Paragraph("MASTER SERVICES AGREEMENT", styles["Title2"]))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(HRFlowable(width="50%", color=colors.HexColor("#0f3460"), thickness=2))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Nextera Technologies Inc. &amp; Atlas Global Solutions LLC", ParagraphStyle("Sub", parent=styles["Normal"], fontSize=13, alignment=TA_CENTER, textColor=colors.HexColor("#333"))))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Contract Value: $12,500,000.00 | Effective Date: March 15, 2025", ParagraphStyle("Sub2", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor("#666"))))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("CONFIDENTIAL - DO NOT DISTRIBUTE", ParagraphStyle("Conf", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER, textColor=colors.red)))
    elements.append(PageBreak())
    
    # Content
    paragraphs = CONTRACT_TEXT.strip().split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        safe = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        if para.startswith("ARTICLE") or para.startswith("RECITALS") or para.startswith("IN WITNESS"):
            elements.append(Paragraph(safe, styles["Section2"]))
        elif para.startswith("MASTER SERVICES"):
            elements.append(Paragraph(safe, styles["Title2"]))
        else:
            elements.append(Paragraph(safe, styles["Body2"]))
    
    doc.build(elements)
    size_kb = os.path.getsize(output) / 1024
    
    # Count pages
    try:
        import fitz
        pages = len(fitz.open(output))
    except:
        pages = "?"
    
    print(f"[OK] Single contract PDF generated!")
    print(f"   Path: {output}")
    print(f"   Size: {size_kb:.0f} KB")
    print(f"   Pages: {pages}")

if __name__ == "__main__":
    build()
