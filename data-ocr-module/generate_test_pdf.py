"""
Legal Contract Repository PDF Generator
Generates a 200+ page PDF with 20 diverse contract types for stress testing
an AI Contract Intelligence platform.
"""
import random
import os
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

# ── Seed for reproducibility ──
random.seed(42)

# ── Data pools ──
COMPANIES = [
    ("Nextera Technologies Inc.", "Delaware", "245 Park Avenue, New York, NY 10167"),
    ("Atlas Global Solutions LLC", "California", "1 Market Street, Suite 3600, San Francisco, CA 94105"),
    ("Pinnacle Software Group Corp.", "Texas", "2200 Ross Avenue, Dallas, TX 75201"),
    ("Meridian Healthcare Partners", "Massachusetts", "100 Federal Street, Boston, MA 02110"),
    ("Summit Financial Services Ltd.", "Illinois", "233 South Wacker Drive, Chicago, IL 60606"),
    ("Horizon Energy Corp.", "Colorado", "1700 Lincoln Street, Denver, CO 80203"),
    ("Vanguard Defense Systems Inc.", "Virginia", "1919 Gallows Road, Vienna, VA 22182"),
    ("Pacific Rim Trading Co.", "Washington", "701 Pike Street, Seattle, WA 98101"),
    ("Sterling Manufacturing LLC", "Michigan", "One Detroit Center, Detroit, MI 48226"),
    ("Catalyst Research Labs", "North Carolina", "100 Main Campus Drive, Durham, NC 27710"),
    ("Orion Aerospace Industries", "Florida", "1000 N. Ashley Drive, Tampa, FL 33602"),
    ("Redwood Consulting Group", "Oregon", "121 SW Morrison Street, Portland, OR 97204"),
    ("Granite Capital Partners", "Connecticut", "One State Street, Hartford, CT 06103"),
    ("Liberty Insurance Holdings", "New Jersey", "200 Park Avenue, Florham Park, NJ 07932"),
    ("Northern Star Logistics Inc.", "Minnesota", "225 South 6th Street, Minneapolis, MN 55402"),
    ("Sapphire Data Solutions", "Georgia", "1075 Peachtree Street NE, Atlanta, GA 30309"),
    ("Evergreen Environmental Corp.", "Arizona", "2398 East Camelback Road, Phoenix, AZ 85016"),
    ("Cobalt Mining International", "Nevada", "3773 Howard Hughes Parkway, Las Vegas, NV 89169"),
    ("Tempest Cybersecurity Inc.", "Maryland", "6116 Executive Boulevard, Rockville, MD 20852"),
    ("Quantum Computing Solutions", "Utah", "15 West South Temple, Salt Lake City, UT 84101"),
    ("Aurora Biotech Ltd.", "Pennsylvania", "1835 Market Street, Philadelphia, PA 19103"),
    ("Silverline Communications", "Ohio", "200 Public Square, Cleveland, OH 44114"),
    ("TrueNorth Analytics Corp.", "Wisconsin", "111 East Wisconsin Avenue, Milwaukee, WI 53202"),
    ("Cascade Water Systems LLC", "Idaho", "800 Park Boulevard, Boise, ID 83712"),
    ("DigitalFront Media Inc.", "New York", "40 Worth Street, New York, NY 10013"),
    ("Ironclad Security Group", "Indiana", "One Indiana Square, Indianapolis, IN 46204"),
    ("Zenith Robotics Corp.", "Tennessee", "150 Fourth Avenue N, Nashville, TN 37219"),
    ("Bluewave Marine Services", "Louisiana", "201 St. Charles Avenue, New Orleans, LA 70170"),
    ("Cornerstone Properties LLC", "Missouri", "211 North Broadway, St. Louis, MO 63102"),
    ("Vertex AI Technologies", "Alabama", "2 20th Street North, Birmingham, AL 35203"),
]

PEOPLE = [
    "James Harrington III", "Sarah Chen-Williams", "Robert J. Fitzgerald",
    "Maria Elena Rodriguez", "David Konstantinos Papas", "Jennifer A. Morrison",
    "Michael K. Tanaka", "Elizabeth O'Brien", "Christopher W. Novak",
    "Amanda Leigh Patterson", "Dr. Thomas P. Worthington", "Catherine M. Sinclair",
    "William R. Abernathy", "Dr. Priya Sharma", "Gregory T. MacDonald",
    "Rachel Goldstein", "Patrick F. Donahue", "Samantha J. Park",
    "Anthony R. Castellano", "Diana L. Thornton", "Marcus D. Washington",
    "Lisa K. Nakamura", "Steven B. Kravitz", "Angela M. DeLuca",
    "Kevin P. Johannsen", "Michelle C. Okafor", "Brian T. Halverson",
    "Stephanie R. Beaumont", "Daniel J. Westmoreland", "Karen A. Fujimoto",
]

EMAILS = [f"{p.split()[0].lower()}.{p.split()[-1].lower().replace(',','')}@{c[0].split()[0].lower()}.com" for p, c in zip(PEOPLE, COMPANIES)]

PHONES = [f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}" for _ in range(30)]

JURISDICTIONS = [
    "State of New York", "State of California", "State of Delaware",
    "State of Texas", "Commonwealth of Massachusetts", "State of Illinois",
    "State of Florida", "State of Colorado", "Commonwealth of Virginia",
    "State of Washington", "State of Georgia", "State of Oregon",
    "State of Connecticut", "State of New Jersey", "State of Minnesota",
    "State of Arizona", "State of Nevada", "State of Maryland",
    "State of Utah", "Commonwealth of Pennsylvania", "State of Ohio",
    "State of Michigan", "State of North Carolina", "State of Tennessee",
    "State of Indiana", "State of Wisconsin", "State of Missouri",
    "State of Louisiana", "State of Alabama", "State of Idaho",
]

GOVERNING_LAWS = [
    "the laws of the State of New York without regard to its conflict of laws principles",
    "the laws of the State of California, excluding its choice of law rules",
    "the laws of the State of Delaware as applied to contracts made and performed entirely within Delaware",
    "the laws of the State of Texas, without giving effect to any choice or conflict of law provision",
    "the laws of the Commonwealth of Massachusetts, without regard to conflicts of laws",
    "the laws of England and Wales",
    "the federal laws of Canada and the laws of the Province of Ontario",
    "the laws of the State of Illinois, without regard to its principles of conflicts of law",
    "the laws of the State of Florida, without giving effect to any choice of law or conflict of law provisions",
    "the laws of the State of Colorado, without regard to its conflict of laws provisions",
]

def rand_date(start_year=2023, end_year=2026):
    d = datetime(start_year, 1, 1) + timedelta(days=random.randint(0, (end_year - start_year) * 365))
    return d.strftime("%B %d, %Y")

def rand_money(low=10000, high=50000000):
    v = random.randint(low, high)
    if v >= 1000000:
        return f"${v:,.2f}"
    return f"${v:,}"

def rand_company_pair():
    a, b = random.sample(COMPANIES, 2)
    return a, b

def rand_person():
    return random.choice(PEOPLE)

def rand_jurisdiction():
    return random.choice(JURISDICTIONS)

def rand_governing_law():
    return random.choice(GOVERNING_LAWS)

# ── Contract generators ──

def gen_software_license(idx):
    c1, c2 = rand_company_pair()
    eff = rand_date()
    val = rand_money(50000, 5000000)
    p1, p2 = rand_person(), rand_person()
    gov = rand_governing_law()
    return f"""SOFTWARE LICENSE AGREEMENT

CONTRACT #{idx:04d}

This Software License Agreement ("Agreement") is entered into as of {eff} ("Effective Date"), by and between:

LICENSOR: {c1[0]}, a corporation organized under the laws of {c1[1]}, with its principal offices at {c1[2]} ("Licensor"), represented by {p1}, Chief Technology Officer, email: {random.choice(EMAILS)}, phone: {random.choice(PHONES)};

AND

LICENSEE: {c2[0]}, a corporation organized under the laws of {c2[1]}, with its principal offices at {c2[2]} ("Licensee"), represented by {p2}, VP of Engineering, email: {random.choice(EMAILS)}, phone: {random.choice(PHONES)}.

RECITALS

WHEREAS, Licensor has developed and owns certain proprietary software known as "{random.choice(['CloudSync Pro', 'DataVault Enterprise', 'SecureNet Platform', 'AnalyticsHub 360', 'ProcessFlow Suite'])}" (the "Software"); and

WHEREAS, Licensee desires to obtain a license to use the Software for its internal business operations; and

WHEREAS, Licensor is willing to grant such license subject to the terms and conditions set forth herein;

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the parties agree as follows:

ARTICLE 1 - DEFINITIONS

1.1 "Authorized Users" means employees, contractors, and agents of Licensee who are authorized to access and use the Software pursuant to this Agreement, not to exceed {random.randint(50, 5000)} users.

1.2 "Documentation" means all user manuals, technical manuals, training materials, specifications, and other written materials provided by Licensor relating to the Software.

1.3 "Intellectual Property Rights" means all patents, copyrights, trademarks, trade secrets, and other intellectual property rights, whether registered or unregistered, relating to the Software.

1.4 "Maintenance and Support" means the technical support and software maintenance services described in Exhibit A attached hereto.

1.5 "Updates" means any bug fixes, patches, minor releases, or other modifications to the Software that Licensor makes generally available to its licensees.

ARTICLE 2 - LICENSE GRANT

2.1 Subject to the terms and conditions of this Agreement, Licensor hereby grants to Licensee a non-exclusive, non-transferable, limited license to install, copy, and use the Software solely for Licensee's internal business purposes during the Term.

2.2 Licensee shall not: (a) sublicense, sell, lease, or otherwise transfer the Software to any third party; (b) modify, adapt, translate, reverse engineer, decompile, or disassemble the Software; (c) create derivative works based on the Software; (d) remove any proprietary notices or labels from the Software; or (e) use the Software for any purpose other than as expressly permitted herein.

2.3 Licensor retains all right, title, and interest in and to the Software, including all Intellectual Property Rights therein. This Agreement does not convey to Licensee any ownership interest in the Software.

ARTICLE 3 - LICENSE FEES AND PAYMENT

3.1 In consideration of the license granted herein, Licensee shall pay to Licensor a total license fee of {val} (the "License Fee"), payable as follows: (a) {rand_money(10000, 500000)} upon execution of this Agreement; (b) the balance in equal quarterly installments over {random.choice([12, 24, 36])} months.

3.2 All payments shall be made in United States Dollars by wire transfer to the account specified by Licensor. Late payments shall bear interest at the rate of {random.choice(['1.0', '1.5', '2.0'])}% per month or the maximum rate permitted by applicable law, whichever is less.

3.3 In addition to the License Fee, Licensee shall pay annual Maintenance and Support fees of {rand_money(5000, 200000)}, payable in advance on each anniversary of the Effective Date.

ARTICLE 4 - CONFIDENTIALITY

4.1 Each party acknowledges that in the course of performing its obligations under this Agreement, it may receive or have access to Confidential Information of the other party. "Confidential Information" means all non-public information disclosed by one party to the other, whether orally, in writing, or by inspection, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure.

4.2 Each party agrees to: (a) hold the other party's Confidential Information in strict confidence; (b) not disclose such Confidential Information to any third party without the prior written consent of the disclosing party; (c) use such Confidential Information only for the purposes of performing its obligations under this Agreement; and (d) protect such Confidential Information using the same degree of care it uses to protect its own confidential information, but in no event less than reasonable care.

4.3 The obligations of confidentiality shall survive the termination or expiration of this Agreement for a period of {random.choice([3, 5, 7])} years.

ARTICLE 5 - WARRANTIES AND DISCLAIMERS

5.1 Licensor warrants that: (a) the Software will perform substantially in accordance with the Documentation for a period of {random.choice([90, 180, 365])} days from delivery; (b) the Software will not infringe upon any third party's intellectual property rights; and (c) Licensor has the full right, power, and authority to enter into this Agreement and grant the license contemplated herein.

5.2 EXCEPT AS EXPRESSLY SET FORTH IN THIS ARTICLE 5, THE SOFTWARE IS PROVIDED "AS IS" AND LICENSOR MAKES NO OTHER WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, OR NON-INFRINGEMENT.

ARTICLE 6 - LIMITATION OF LIABILITY

6.1 IN NO EVENT SHALL EITHER PARTY BE LIABLE TO THE OTHER PARTY FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, LOSS OF DATA, BUSINESS INTERRUPTION, OR LOSS OF GOODWILL, REGARDLESS OF THE CAUSE OF ACTION OR THE THEORY OF LIABILITY, EVEN IF SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

6.2 THE TOTAL AGGREGATE LIABILITY OF LICENSOR UNDER THIS AGREEMENT SHALL NOT EXCEED THE TOTAL AMOUNT OF FEES ACTUALLY PAID BY LICENSEE TO LICENSOR DURING THE TWELVE (12) MONTH PERIOD PRECEDING THE EVENT GIVING RISE TO THE CLAIM.

ARTICLE 7 - INDEMNIFICATION

7.1 Licensor shall indemnify, defend, and hold harmless Licensee, its officers, directors, employees, agents, and successors from and against any and all third-party claims, demands, suits, proceedings, losses, damages, liabilities, costs, and expenses (including reasonable attorneys' fees) arising out of or relating to any claim that the Software infringes any patent, copyright, trademark, or trade secret of any third party.

7.2 Licensee shall indemnify, defend, and hold harmless Licensor from and against any claims arising out of Licensee's use of the Software in violation of this Agreement or applicable law.

ARTICLE 8 - TERMINATION

8.1 This Agreement shall commence on the Effective Date and continue for an initial term of {random.choice([1, 2, 3, 5])} year(s) (the "Initial Term"), unless earlier terminated in accordance with this Article.

8.2 Either party may terminate this Agreement: (a) upon {random.choice([30, 60, 90])} days' prior written notice to the other party; (b) immediately upon written notice if the other party commits a material breach and fails to cure such breach within {random.choice([15, 30, 45])} days after receipt of written notice; or (c) immediately if the other party becomes insolvent, files for bankruptcy, or ceases to conduct business.

8.3 Upon termination or expiration of this Agreement, Licensee shall immediately cease all use of the Software, destroy all copies thereof, and certify in writing to Licensor that it has done so.

ARTICLE 9 - GOVERNING LAW AND DISPUTE RESOLUTION

9.1 This Agreement shall be governed by and construed in accordance with {gov}.

9.2 Any dispute arising out of or relating to this Agreement shall first be submitted to good faith negotiations between senior executives of each party. If the dispute cannot be resolved through negotiation within {random.choice([30, 45, 60])} days, either party may submit the dispute to binding arbitration administered by the American Arbitration Association under its Commercial Arbitration Rules.

9.3 The arbitration shall take place in {random.choice(['New York, New York', 'San Francisco, California', 'Chicago, Illinois', 'Dallas, Texas', 'Boston, Massachusetts'])}, and the arbitrator's decision shall be final and binding.

ARTICLE 10 - GENERAL PROVISIONS

10.1 Force Majeure. Neither party shall be liable for any delay or failure to perform its obligations under this Agreement due to causes beyond its reasonable control, including but not limited to acts of God, war, terrorism, epidemics, pandemics, government actions, fire, flood, earthquake, labor disputes, or Internet or telecommunications failures.

10.2 Entire Agreement. This Agreement, together with all Exhibits attached hereto, constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior agreements, understandings, negotiations, and discussions, whether oral or written.

10.3 Assignment. Neither party may assign this Agreement or any of its rights or obligations hereunder without the prior written consent of the other party, except that either party may assign this Agreement in connection with a merger, acquisition, or sale of all or substantially all of its assets.

10.4 Notices. All notices required or permitted under this Agreement shall be in writing and shall be deemed given when delivered personally, sent by confirmed facsimile, sent by certified or registered mail (postage prepaid, return receipt requested), or sent by recognized overnight courier.

10.5 Severability. If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall continue in full force and effect.

10.6 Waiver. No waiver of any provision of this Agreement shall be effective unless in writing and signed by the waiving party.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

LICENSOR: {c1[0]}
By: ____________________________
Name: {p1}
Title: Chief Technology Officer
Date: {eff}

LICENSEE: {c2[0]}
By: ____________________________
Name: {p2}
Title: VP of Engineering
Date: {eff}

"""

def gen_nda(idx):
    c1, c2 = rand_company_pair()
    eff = rand_date()
    p1, p2 = rand_person(), rand_person()
    gov = rand_governing_law()
    return f"""NON-DISCLOSURE AGREEMENT

CONTRACT #{idx:04d}

This Non-Disclosure Agreement ("Agreement") is entered into as of {eff} ("Effective Date"), by and between:

DISCLOSING PARTY: {c1[0]}, organized under the laws of {c1[1]}, located at {c1[2]}, represented by {p1}, General Counsel, email: {random.choice(EMAILS)}, phone: {random.choice(PHONES)} ("Disclosing Party");

AND

RECEIVING PARTY: {c2[0]}, organized under the laws of {c2[1]}, located at {c2[2]}, represented by {p2}, Director of Business Development, email: {random.choice(EMAILS)}, phone: {random.choice(PHONES)} ("Receiving Party").

RECITALS

WHEREAS, the Disclosing Party possesses certain confidential and proprietary information relating to its business operations, technology, financial data, customer lists, strategic plans, and trade secrets; and

WHEREAS, the Receiving Party desires to receive certain of such information for the purpose of evaluating a potential business relationship between the parties (the "Purpose"); and

WHEREAS, the Disclosing Party is willing to disclose such information subject to the terms of this Agreement;

NOW, THEREFORE, in consideration of the mutual promises contained herein, the parties agree:

SECTION 1 - DEFINITION OF CONFIDENTIAL INFORMATION

1.1 "Confidential Information" means all information, in any form or medium, whether written, oral, electronic, visual, or otherwise, that is disclosed by the Disclosing Party to the Receiving Party, including but not limited to: (a) business plans, financial statements, projections, and budgets; (b) customer and supplier lists, pricing information, and sales data; (c) technical data, specifications, designs, algorithms, source code, and know-how; (d) marketing strategies, product roadmaps, and competitive analyses; (e) employee information and organizational structures; (f) legal strategies and pending litigation; and (g) any information marked as "Confidential," "Proprietary," or with a similar designation.

1.2 Confidential Information shall not include information that: (a) was publicly available at the time of disclosure; (b) becomes publicly available through no fault of the Receiving Party; (c) was rightfully in the Receiving Party's possession prior to disclosure; (d) is independently developed by the Receiving Party without use of the Confidential Information; or (e) is rightfully obtained from a third party without restriction on disclosure.

SECTION 2 - OBLIGATIONS OF RECEIVING PARTY

2.1 The Receiving Party shall: (a) hold the Confidential Information in strict confidence and not disclose it to any third party without the prior written consent of the Disclosing Party; (b) use the Confidential Information solely for the Purpose; (c) limit access to the Confidential Information to those of its employees, agents, and advisors who have a need to know and who are bound by confidentiality obligations no less restrictive than those contained herein; (d) protect the Confidential Information using at least the same degree of care it uses to protect its own confidential information, but in no event less than reasonable care; and (e) promptly notify the Disclosing Party of any unauthorized disclosure or use of the Confidential Information.

2.2 The Receiving Party may disclose Confidential Information if required by law, regulation, or court order, provided that the Receiving Party: (a) gives the Disclosing Party prompt written notice of such requirement; (b) cooperates with the Disclosing Party's efforts to obtain a protective order; and (c) discloses only the minimum amount of Confidential Information required.

SECTION 3 - TERM AND TERMINATION

3.1 This Agreement shall commence on the Effective Date and continue for a period of {random.choice([2, 3, 5])} years unless earlier terminated by either party upon {random.choice([15, 30])} days' written notice.

3.2 The obligations of confidentiality shall survive the termination or expiration of this Agreement for an additional period of {random.choice([3, 5, 7, 10])} years.

3.3 Upon termination or request by the Disclosing Party, the Receiving Party shall promptly return or destroy all copies of the Confidential Information and certify in writing that it has done so.

SECTION 4 - REMEDIES

4.1 The Receiving Party acknowledges that any unauthorized disclosure or use of the Confidential Information may cause irreparable harm to the Disclosing Party for which monetary damages would be inadequate. Accordingly, the Disclosing Party shall be entitled to seek injunctive relief, specific performance, or other equitable remedies, in addition to any other remedies available at law or in equity.

4.2 In the event of a breach, the breaching party shall be liable for all direct damages, including reasonable attorneys' fees and costs incurred by the non-breaching party.

SECTION 5 - NO LICENSE; NO WARRANTY

5.1 Nothing in this Agreement shall be construed as granting to the Receiving Party any license, ownership right, or other interest in the Confidential Information.

5.2 ALL CONFIDENTIAL INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

SECTION 6 - GOVERNING LAW

6.1 This Agreement shall be governed by and construed in accordance with {gov}.

6.2 Any dispute arising under this Agreement shall be resolved by binding arbitration in {random.choice(['New York', 'San Francisco', 'Chicago', 'Los Angeles', 'Boston'])}, {random.choice(JURISDICTIONS)}.

SECTION 7 - MISCELLANEOUS

7.1 This Agreement constitutes the entire agreement between the parties regarding the subject matter hereof.

7.2 This Agreement may not be amended except by a written instrument signed by both parties.

7.3 Neither party may assign this Agreement without the prior written consent of the other party.

7.4 If any provision of this Agreement is held unenforceable, the remaining provisions shall continue in full force.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

DISCLOSING PARTY: {c1[0]}
By: ____________________________
Name: {p1}
Title: General Counsel
Date: {eff}

RECEIVING PARTY: {c2[0]}
By: ____________________________
Name: {p2}
Title: Director of Business Development
Date: {eff}

"""

def gen_employment(idx):
    c1 = random.choice(COMPANIES)
    emp = rand_person()
    eff = rand_date()
    salary = rand_money(60000, 350000)
    bonus = rand_money(5000, 100000)
    gov = rand_governing_law()
    return f"""EMPLOYMENT AGREEMENT

CONTRACT #{idx:04d}

This Employment Agreement ("Agreement") is made and entered into as of {eff}, by and between:

EMPLOYER: {c1[0]}, a corporation organized under the laws of {c1[1]}, with its principal offices at {c1[2]}, phone: {random.choice(PHONES)}, email: hr@{c1[0].split()[0].lower()}.com ("Employer" or "Company");

AND

EMPLOYEE: {emp}, an individual residing at {random.randint(100,9999)} {random.choice(['Oak', 'Elm', 'Maple', 'Pine', 'Cedar'])} {random.choice(['Street', 'Avenue', 'Drive', 'Boulevard', 'Lane'])}, {random.choice(['Apartment', 'Suite', 'Unit'])} {random.randint(1,500)}, {random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])}, {random.choice(['NY', 'CA', 'IL', 'TX', 'AZ'])} {random.randint(10000,99999)}, SSN: XXX-XX-{random.randint(1000,9999)}, phone: {random.choice(PHONES)}, email: {emp.split()[0].lower()}@email.com ("Employee").

RECITALS

WHEREAS, the Company desires to employ the Employee in the position of {random.choice(['Senior Vice President', 'Director of Engineering', 'Chief Financial Officer', 'Vice President of Sales', 'Head of Product', 'General Manager', 'Chief Operating Officer', 'Senior Director'])}, and the Employee desires to accept such employment, subject to the terms and conditions set forth herein;

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree:

ARTICLE 1 - POSITION AND DUTIES

1.1 The Company hereby employs the Employee as {random.choice(['Senior Vice President', 'Director of Engineering', 'Chief Financial Officer'])} ("Position"), reporting to the {random.choice(['Chief Executive Officer', 'President', 'Board of Directors'])}.

1.2 The Employee shall devote substantially all of the Employee's business time, attention, skill, and energy to the performance of the Employee's duties and shall faithfully and diligently serve the Company.

1.3 The Employee's principal place of employment shall be at the Company's offices located at {c1[2]}, subject to travel requirements as reasonably necessary.

ARTICLE 2 - COMPENSATION

2.1 Base Salary. The Company shall pay the Employee an annual base salary of {salary} ("Base Salary"), payable in accordance with the Company's standard payroll practices, less applicable withholdings and deductions.

2.2 Annual Bonus. The Employee shall be eligible for an annual performance bonus of up to {bonus} ("Annual Bonus"), based upon the achievement of individual and company performance objectives as determined by the Board of Directors.

2.3 Equity Compensation. The Employee shall be granted {random.randint(1000, 50000)} stock options under the Company's Equity Incentive Plan, vesting over {random.choice([3, 4])} years with a one-year cliff, at a strike price to be determined by the Board.

2.4 Benefits. The Employee shall be eligible to participate in all employee benefit plans, programs, and arrangements made available to senior executives, including health insurance, dental insurance, vision insurance, life insurance ({rand_money(100000, 1000000)} coverage), disability insurance, and 401(k) retirement plan with Company matching of up to {random.choice([3, 4, 5, 6])}% of salary.

2.5 Paid Time Off. The Employee shall receive {random.choice([20, 25, 30])} days of paid vacation per year, in addition to Company-observed holidays and {random.choice([5, 10])} days of sick leave.

2.6 Relocation. The Company shall provide a one-time relocation allowance of up to {rand_money(10000, 75000)} for expenses incurred in connection with the Employee's relocation.

ARTICLE 3 - TERM AND TERMINATION

3.1 This Agreement shall be effective as of the Effective Date and shall continue until terminated as provided herein. The initial term shall be {random.choice([2, 3])} years (the "Initial Term").

3.2 Termination Without Cause. The Company may terminate the Employee's employment without Cause upon {random.choice([30, 60, 90])} days' prior written notice. In such event, the Employee shall be entitled to: (a) continuation of Base Salary for {random.choice([6, 9, 12, 18])} months; (b) payment of a prorated Annual Bonus; (c) continued health insurance benefits for {random.choice([6, 12, 18])} months (COBRA); and (d) accelerated vesting of {random.choice([25, 50, 100])}% of unvested equity.

3.3 Termination for Cause. The Company may terminate the Employee's employment immediately for Cause. "Cause" means: (a) material breach of this Agreement; (b) conviction of a felony; (c) willful misconduct or gross negligence; (d) fraud, embezzlement, or theft; or (e) failure to perform duties after written notice and {random.choice([15, 30])} days to cure.

3.4 Resignation. The Employee may resign upon {random.choice([30, 60, 90])} days' prior written notice.

3.5 Change of Control. In the event of a Change of Control (as defined below) and the Employee's termination within {random.choice([12, 18, 24])} months following such Change of Control, the Employee shall receive: (a) a lump-sum severance payment equal to {random.choice([1, 1.5, 2, 3])} times the Employee's annual Base Salary; (b) full acceleration of all unvested equity; and (c) continued benefits for {random.choice([12, 18, 24])} months.

ARTICLE 4 - CONFIDENTIALITY

4.1 The Employee acknowledges that during the course of employment, the Employee will have access to and become acquainted with Confidential Information belonging to the Company. The Employee agrees to hold all Confidential Information in strict confidence and not disclose or use such information except as required in the performance of duties.

4.2 This obligation of confidentiality shall survive the termination of employment for a period of {random.choice([3, 5, 7])} years.

ARTICLE 5 - NON-COMPETITION AND NON-SOLICITATION

5.1 Non-Competition. During the term of employment and for a period of {random.choice([6, 12, 18, 24])} months following termination, the Employee shall not engage in or provide services to any Competing Business within the {random.choice(['United States', 'North America', 'worldwide'])} territory.

5.2 Non-Solicitation. For a period of {random.choice([12, 18, 24])} months following termination, the Employee shall not directly or indirectly solicit or recruit any employee, consultant, or customer of the Company.

ARTICLE 6 - INTELLECTUAL PROPERTY

6.1 All Work Product (inventions, designs, works of authorship, developments, improvements, trade secrets, and discoveries) created by the Employee during employment shall be the sole property of the Company.

6.2 The Employee hereby assigns all rights, title, and interest in any Work Product to the Company.

ARTICLE 7 - GOVERNING LAW

7.1 This Agreement shall be governed by and construed in accordance with {gov}.

7.2 Any dispute shall be resolved through binding arbitration in {random.choice(['New York', 'San Francisco', 'Chicago', 'Dallas'])} under the rules of the American Arbitration Association.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

EMPLOYER: {c1[0]}
By: ____________________________
Name: {random.choice(PEOPLE)}
Title: Chief Executive Officer
Date: {eff}

EMPLOYEE:
By: ____________________________
Name: {emp}
Date: {eff}

"""

def gen_saas_agreement(idx):
    c1, c2 = rand_company_pair()
    eff = rand_date()
    val = rand_money(20000, 2000000)
    p1, p2 = rand_person(), rand_person()
    gov = rand_governing_law()
    high_risk = random.random() > 0.5
    return f"""SAAS SUBSCRIPTION AGREEMENT

CONTRACT #{idx:04d}

This SaaS Subscription Agreement ("Agreement") is entered into as of {eff} by and between:

PROVIDER: {c1[0]}, organized under the laws of {c1[1]}, with offices at {c1[2]}, email: sales@{c1[0].split()[0].lower()}.com, phone: {random.choice(PHONES)} ("Provider");

AND

SUBSCRIBER: {c2[0]}, organized under the laws of {c2[1]}, with offices at {c2[2]}, email: procurement@{c2[0].split()[0].lower()}.com, phone: {random.choice(PHONES)} ("Subscriber").

Authorized Representatives: {p1} (Provider) and {p2} (Subscriber).

ARTICLE 1 - SERVICE DESCRIPTION

1.1 Provider shall make available to Subscriber a cloud-based {random.choice(['enterprise resource planning', 'customer relationship management', 'human capital management', 'supply chain management', 'business intelligence', 'project management'])} platform (the "Service") accessible via {random.choice(['https://portal.provider.com', 'https://app.service.com', 'https://cloud.platform.com'])}.

1.2 The Service shall include: (a) core application functionality as described in Exhibit A; (b) data storage of up to {random.choice(['500 GB', '1 TB', '5 TB', '10 TB'])}; (c) API access with rate limits of {random.randint(1000, 100000)} requests per hour; and (d) {random.choice([24, 12, 8])}/7 technical support.

ARTICLE 2 - SUBSCRIPTION FEES

2.1 Subscriber shall pay Provider annual subscription fees of {val} ("Subscription Fee"), payable {random.choice(['annually in advance', 'quarterly in advance', 'monthly in advance'])}.

2.2 {"AUTOMATIC RENEWAL AND PRICE ESCALATION: The subscription shall automatically renew for successive one-year periods unless terminated with 90 days notice. Provider may increase fees by up to 15% upon each renewal without consent." if high_risk else "Renewal: This Agreement shall renew for additional one-year periods upon mutual written agreement. Any fee changes require 60 days prior written notice and Subscriber consent."}

2.3 Late Payment. Payments not received within {random.choice([15, 30])} days shall incur a late fee of {random.choice(['1.5', '2.0', '2.5'])}% per month. {"Provider may suspend Service access after 15 days of non-payment without prior notice." if high_risk else "Provider shall provide 30 days written notice before any service suspension for non-payment."}

ARTICLE 3 - SERVICE LEVEL AGREEMENT

3.1 Provider guarantees an uptime of {random.choice(['99.5', '99.9', '99.95', '99.99'])}% measured on a monthly basis, excluding scheduled maintenance.

3.2 {"Service credits shall be Provider's sole and exclusive remedy for any downtime, capped at 10% of monthly fees." if high_risk else "Service Credits: For each 0.1% below the guaranteed uptime, Subscriber shall receive a service credit equal to 5% of the monthly Subscription Fee, up to a maximum of 100% of the monthly fee."}

3.3 Scheduled maintenance windows shall be {random.choice(['Sundays 2:00 AM - 6:00 AM EST', 'Saturdays 11:00 PM - 3:00 AM PST', 'Tuesdays 1:00 AM - 5:00 AM CST'])} with {random.choice([48, 72])} hours advance notice.

ARTICLE 4 - DATA PRIVACY AND SECURITY

4.1 Provider shall process Subscriber data in accordance with all applicable data protection laws, including but not limited to GDPR, CCPA, HIPAA (if applicable), and SOC 2 Type II requirements.

4.2 Provider shall maintain commercially reasonable administrative, physical, and technical safeguards, including {random.choice(['AES-256', 'AES-128'])} encryption at rest and TLS 1.3 encryption in transit.

4.3 Data Breach Notification. Provider shall notify Subscriber of any confirmed data breach within {random.choice([24, 48, 72])} hours of discovery.

4.4 Data Location. Subscriber data shall be stored in {random.choice(['US-based data centers only', 'AWS US-East-1 and US-West-2 regions', 'Azure US regions', 'Google Cloud US regions'])}. Provider shall not transfer data outside the United States without prior written consent.

4.5 {"Data Ownership: Provider retains a perpetual, irrevocable license to use anonymized and aggregated Subscriber data for any purpose including sale to third parties." if high_risk else "Data Ownership: All Subscriber data remains the sole property of Subscriber. Provider shall not use, sell, or share Subscriber data for any purpose other than providing the Service."}

ARTICLE 5 - INTELLECTUAL PROPERTY

5.1 Provider retains all intellectual property rights in the Service. Subscriber retains all intellectual property rights in its data.

5.2 {"Any customizations, integrations, or configurations developed by Subscriber using the Service shall become the property of Provider." if high_risk else "Any customizations or configurations created by Subscriber shall remain the property of Subscriber."}

ARTICLE 6 - INDEMNIFICATION

6.1 {"Subscriber shall indemnify, defend, and hold harmless Provider from ALL claims, damages, losses, costs, and expenses (including attorneys' fees) arising from ANY use of the Service, regardless of fault." if high_risk else "Each party shall indemnify the other against third-party claims arising from that party's breach of this Agreement or negligent acts."}

6.2 Provider shall indemnify Subscriber against claims that the Service infringes any third-party intellectual property right.

ARTICLE 7 - LIMITATION OF LIABILITY

7.1 {"PROVIDER'S TOTAL AGGREGATE LIABILITY SHALL NOT EXCEED THE FEES PAID BY SUBSCRIBER IN THE THREE (3) MONTHS PRECEDING THE CLAIM." if high_risk else "THE TOTAL AGGREGATE LIABILITY OF EITHER PARTY SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE DURING THE TWELVE (12) MONTH PERIOD PRECEDING THE CLAIM."}

7.2 IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES.

ARTICLE 8 - TERMINATION

8.1 {"This Agreement may only be terminated by Subscriber upon 180 days prior written notice, with payment of an early termination fee equal to 50% of the remaining contract value." if high_risk else "Either party may terminate upon 60 days written notice or immediately upon material breach that remains uncured for 30 days."}

8.2 Upon termination, Provider shall make Subscriber's data available for export for a period of {random.choice([30, 60, 90])} days, after which all data shall be permanently deleted.

ARTICLE 9 - AUDIT RIGHTS

9.1 {"Provider shall have the right to audit Subscriber's use of the Service at any time, without notice, and Subscriber shall bear all costs of such audit." if high_risk else "Each party may audit the other's compliance with this Agreement upon 30 days' prior written notice, at the auditing party's expense, no more than once per year."}

ARTICLE 10 - GOVERNING LAW

10.1 This Agreement shall be governed by {gov}.

10.2 Any disputes shall be resolved through binding arbitration in {random.choice(['New York', 'San Francisco', 'Chicago', 'Dallas', 'Boston', 'Denver'])}.

ARTICLE 11 - INSURANCE REQUIREMENTS

11.1 Provider shall maintain: (a) Commercial General Liability insurance with limits of not less than {rand_money(1000000, 5000000)} per occurrence; (b) Professional Liability / E&O insurance of not less than {rand_money(2000000, 10000000)}; (c) Cyber Liability insurance of not less than {rand_money(5000000, 20000000)}; and (d) Workers' Compensation insurance as required by law.

IN WITNESS WHEREOF, the parties have executed this Agreement.

PROVIDER: {c1[0]}
By: ____________________________
Name: {p1}
Title: Chief Revenue Officer
Date: {eff}

SUBSCRIBER: {c2[0]}
By: ____________________________
Name: {p2}
Title: Chief Information Officer
Date: {eff}

"""

# ── Additional contract generators (shorter) ──

def gen_vendor(idx): return gen_generic("VENDOR AGREEMENT", idx, "Vendor", "Client", "supply goods and/or services")
def gen_procurement(idx): return gen_generic("PROCUREMENT CONTRACT", idx, "Supplier", "Purchaser", "procure and deliver materials and equipment")
def gen_sla(idx): return gen_generic("SERVICE LEVEL AGREEMENT", idx, "Service Provider", "Customer", "provide managed IT services with guaranteed uptime")
def gen_professional(idx): return gen_generic("PROFESSIONAL SERVICES AGREEMENT", idx, "Consultant", "Client", "provide professional consulting services")
def gen_consulting(idx): return gen_generic("CONSULTING AGREEMENT", idx, "Consulting Firm", "Engagement Client", "provide strategic consulting and advisory services")
def gen_partnership(idx): return gen_generic("PARTNERSHIP AGREEMENT", idx, "Partner A", "Partner B", "form a general partnership for joint business operations")
def gen_joint_venture(idx): return gen_generic("JOINT VENTURE AGREEMENT", idx, "JV Partner Alpha", "JV Partner Beta", "establish a joint venture for collaborative project development")
def gen_franchise(idx): return gen_generic("FRANCHISE AGREEMENT", idx, "Franchisor", "Franchisee", "grant a franchise license to operate branded retail locations")
def gen_real_estate(idx): return gen_generic("COMMERCIAL LEASE AGREEMENT", idx, "Landlord", "Tenant", "lease commercial office space")
def gen_loan(idx): return gen_generic("LOAN AGREEMENT", idx, "Lender", "Borrower", "provide a term loan facility")
def gen_insurance(idx): return gen_generic("INSURANCE AGREEMENT", idx, "Insurer", "Policyholder", "provide commercial insurance coverage")
def gen_manufacturing(idx): return gen_generic("MANUFACTURING AGREEMENT", idx, "Manufacturer", "Brand Owner", "manufacture products according to specifications")
def gen_distribution(idx): return gen_generic("DISTRIBUTION AGREEMENT", idx, "Distributor", "Manufacturer", "distribute products within designated territories")
def gen_reseller(idx): return gen_generic("RESELLER AGREEMENT", idx, "Vendor", "Authorized Reseller", "resell software products and services")
def gen_data_processing(idx): return gen_generic("DATA PROCESSING AGREEMENT", idx, "Data Controller", "Data Processor", "process personal data in compliance with GDPR and applicable privacy laws")
def gen_cloud(idx): return gen_generic("CLOUD SERVICE AGREEMENT", idx, "Cloud Provider", "Enterprise Customer", "provide cloud infrastructure and platform services")

def gen_generic(title, idx, role1, role2, purpose):
    c1, c2 = rand_company_pair()
    eff = rand_date()
    val = rand_money(25000, 15000000)
    p1, p2 = rand_person(), rand_person()
    gov = rand_governing_law()
    high_risk = random.random() > 0.6
    dur = random.choice([1, 2, 3, 5])
    
    sections = f"""{title}

CONTRACT #{idx:04d}

This {title.title()} ("Agreement") is entered into as of {eff} ("Effective Date"), by and between:

{role1.upper()}: {c1[0]}, a corporation organized under the laws of {c1[1]}, with its principal offices at {c1[2]}, represented by {p1}, {random.choice(['CEO', 'COO', 'SVP', 'General Manager', 'Managing Director'])}, email: {random.choice(EMAILS)}, phone: {random.choice(PHONES)} ("{role1}");

AND

{role2.upper()}: {c2[0]}, a corporation organized under the laws of {c2[1]}, with its principal offices at {c2[2]}, represented by {p2}, {random.choice(['VP of Operations', 'Director of Procurement', 'Chief Legal Officer', 'Head of Partnerships'])}, email: {random.choice(EMAILS)}, phone: {random.choice(PHONES)} ("{role2}").

RECITALS

WHEREAS, the {role1} is engaged in the business of providing specialized products and services; and WHEREAS, the {role2} desires to engage the {role1} to {purpose}; and WHEREAS, the parties wish to set forth the terms and conditions of their relationship;

NOW, THEREFORE, in consideration of the mutual covenants and agreements herein, the parties agree:

ARTICLE 1 - SCOPE OF WORK

1.1 The {role1} shall {purpose} as more fully described in the Statement of Work attached hereto as Exhibit A and incorporated herein by reference.

1.2 The {role1} shall perform all services in a professional and workmanlike manner, consistent with industry standards and best practices, and in compliance with all applicable laws, regulations, and ordinances.

1.3 The {role1} shall assign qualified personnel with relevant experience and expertise to perform the work. Key personnel shall not be reassigned without prior written approval of the {role2}.

1.4 The {role1} shall maintain accurate records of all work performed, materials used, and expenses incurred in connection with this Agreement, and shall make such records available for inspection upon reasonable notice.

ARTICLE 2 - COMPENSATION AND PAYMENT TERMS

2.1 Total Contract Value. The total compensation payable under this Agreement shall not exceed {val} (the "Contract Value"), inclusive of all fees, expenses, and applicable taxes.

2.2 Payment Schedule. The {role2} shall pay the {role1} according to the following schedule: (a) {rand_money(5000, 200000)} upon execution of this Agreement as a mobilization payment; (b) monthly progress payments based on completed milestones; (c) {random.choice([5, 10, 15])}% retention to be released upon final acceptance.

2.3 Invoicing. The {role1} shall submit detailed invoices on a monthly basis. Each invoice shall include: itemized description of services performed, hours worked (if applicable), expenses incurred with supporting documentation, and applicable taxes.

2.4 Payment Terms. The {role2} shall pay all undisputed invoices within {random.choice([30, 45, 60])} days of receipt. Late payments shall accrue interest at {random.choice(['1.0', '1.5', '2.0'])}% per month.

2.5 {"PRICE ESCALATION: The {role1} may increase prices by up to 20% annually without consent." if high_risk else f"Price Adjustments: Any changes to the Contract Value require mutual written agreement executed by authorized representatives of both parties."}

ARTICLE 3 - TERM AND RENEWAL

3.1 This Agreement shall commence on the Effective Date and continue for an initial term of {dur} year(s) (the "Initial Term").

3.2 {"AUTOMATIC RENEWAL: This Agreement shall automatically renew for successive {dur}-year periods unless the {role2} provides written notice of non-renewal at least 180 days prior to the end of the then-current term." if high_risk else f"Renewal: This Agreement may be renewed for additional {dur}-year periods upon mutual written agreement of the parties, executed at least 60 days prior to expiration."}

ARTICLE 4 - TERMINATION

4.1 Termination for Convenience. {"Only the {role1} may terminate this Agreement for convenience upon 30 days notice. The {role2} may not terminate for convenience and shall pay the full remaining contract value as liquidated damages." if high_risk else f"Either party may terminate this Agreement for convenience upon {random.choice([30, 60, 90])} days' prior written notice to the other party."}

4.2 Termination for Cause. Either party may terminate this Agreement immediately upon written notice if: (a) the other party commits a material breach and fails to cure such breach within {random.choice([15, 30, 45])} days after written notice; (b) the other party becomes insolvent or files for bankruptcy; or (c) the other party is convicted of fraud or criminal misconduct.

4.3 Effect of Termination. Upon termination: (a) all rights granted hereunder shall immediately cease; (b) the {role1} shall deliver all work product and materials to the {role2}; (c) the {role2} shall pay for all services performed and expenses incurred through the date of termination; and (d) all confidentiality, indemnification, and limitation of liability provisions shall survive.

ARTICLE 5 - CONFIDENTIALITY

5.1 Each party shall hold in strict confidence all Confidential Information of the other party and shall not disclose such information to any third party without prior written consent, except to employees, agents, and advisors who have a need to know and are bound by confidentiality obligations.

5.2 Confidential Information shall not include information that: (a) is or becomes publicly available through no fault of the receiving party; (b) was in the receiving party's possession prior to disclosure; (c) is independently developed; or (d) is rightfully obtained from a third party.

5.3 The obligations of confidentiality shall survive termination for {random.choice([3, 5, 7])} years.

ARTICLE 6 - INTELLECTUAL PROPERTY

6.1 {"All work product, deliverables, inventions, and intellectual property created during the performance of this Agreement shall be the sole and exclusive property of the {role1}, with the {role2} receiving only a limited, revocable license to use such materials." if high_risk else f"All work product, deliverables, and intellectual property created specifically for the {role2} under this Agreement shall be the sole property of the {role2}. The {role1} retains ownership of pre-existing intellectual property."}

6.2 The {role1} represents and warrants that the deliverables shall not infringe upon any third party's intellectual property rights.

ARTICLE 7 - INDEMNIFICATION

7.1 {"The {role2} shall indemnify, defend, and hold harmless the {role1} and its affiliates, officers, directors, employees, and agents from and against ANY AND ALL claims, damages, losses, costs, and expenses (including attorneys' fees) arising from or related to this Agreement, regardless of fault, negligence, or cause." if high_risk else f"Each party shall indemnify, defend, and hold harmless the other party from claims arising from: (a) the indemnifying party's breach of this Agreement; (b) the indemnifying party's negligence or willful misconduct; or (c) any violation of applicable law by the indemnifying party."}

7.2 The indemnifying party shall have the right to control the defense of any claim and the indemnified party shall cooperate and provide reasonable assistance.

ARTICLE 8 - LIABILITY

8.1 {"THE {role1}'S TOTAL LIABILITY SHALL BE LIMITED TO THE FEES PAID IN THE 3 MONTHS PRIOR TO THE CLAIM. THE {role2}'S LIABILITY SHALL BE UNLIMITED." if high_risk else f"THE TOTAL AGGREGATE LIABILITY OF EITHER PARTY SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE UNDER THIS AGREEMENT DURING THE 12-MONTH PERIOD PRECEDING THE CLAIM."}

8.2 IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOSS OF PROFITS, LOSS OF DATA, OR BUSINESS INTERRUPTION.

{"8.3 NOTWITHSTANDING THE FOREGOING, THE LIMITATION OF LIABILITY SHALL NOT APPLY TO: (a) BREACHES OF CONFIDENTIALITY; (b) INDEMNIFICATION OBLIGATIONS; OR (c) INTENTIONAL MISCONDUCT." if not high_risk else ""}

ARTICLE 9 - INSURANCE

9.1 The {role1} shall maintain the following insurance coverage throughout the term: (a) Commercial General Liability: {rand_money(1000000, 5000000)} per occurrence / {rand_money(2000000, 10000000)} aggregate; (b) Professional Liability / Errors & Omissions: {rand_money(1000000, 10000000)} per claim; (c) Workers' Compensation: as required by applicable law; (d) Commercial Auto Liability: {rand_money(500000, 2000000)} combined single limit; {"(e) Cyber Liability: " + rand_money(5000000, 25000000) + " per incident;" if random.random() > 0.5 else ""} (f) Umbrella/Excess Liability: {rand_money(5000000, 25000000)}.

9.2 The {role1} shall name the {role2} as an additional insured on its Commercial General Liability policy and shall provide certificates of insurance upon request.

ARTICLE 10 - AUDIT RIGHTS

10.1 {"The {role2} shall grant the {role1} unlimited audit rights, including the right to audit at any time without notice, and shall bear all costs associated with any audit regardless of findings." if high_risk else f"Each party may, upon 30 days' prior written notice, audit the other party's compliance with this Agreement. Audits shall be conducted during normal business hours, no more than once per calendar year, and at the auditing party's expense unless the audit reveals a material discrepancy of 5% or more."}

ARTICLE 11 - FORCE MAJEURE

11.1 Neither party shall be liable for any delay or failure to perform its obligations under this Agreement to the extent that such delay or failure is caused by Force Majeure Events, including but not limited to: acts of God, war, terrorism, civil unrest, epidemics, pandemics, government orders or regulations, natural disasters (earthquake, hurricane, flood, fire), labor strikes or lockouts, power failures, telecommunications failures, supply chain disruptions, or other events beyond the reasonable control of the affected party.

11.2 The affected party shall: (a) promptly notify the other party of the Force Majeure Event; (b) use reasonable efforts to mitigate the effects; and (c) resume performance as soon as reasonably practicable. If a Force Majeure Event continues for more than {random.choice([60, 90, 120, 180])} days, either party may terminate this Agreement upon written notice.

ARTICLE 12 - DATA PRIVACY AND COMPLIANCE

12.1 Each party shall comply with all applicable data protection and privacy laws, including GDPR, CCPA, HIPAA (where applicable), and other applicable regulations.

12.2 If the {role1} processes personal data on behalf of the {role2}, the parties shall enter into a Data Processing Agreement substantially in the form attached as Exhibit B.

12.3 The {role1} shall implement appropriate technical and organizational measures to protect personal data against unauthorized access, alteration, disclosure, or destruction.

ARTICLE 13 - GOVERNING LAW AND DISPUTE RESOLUTION

13.1 This Agreement shall be governed by and construed in accordance with {gov}.

13.2 The parties shall first attempt to resolve disputes through good faith negotiation. If unresolved within {random.choice([30, 45, 60])} days, disputes shall be submitted to binding arbitration under the rules of the {random.choice(['American Arbitration Association', 'JAMS', 'International Chamber of Commerce'])} in {random.choice(['New York, NY', 'San Francisco, CA', 'Chicago, IL', 'Dallas, TX', 'Boston, MA', 'Denver, CO', 'Miami, FL', 'Atlanta, GA', 'Seattle, WA', 'Los Angeles, CA'])}.

13.3 The prevailing party shall be entitled to recover reasonable attorneys' fees and costs from the non-prevailing party.

ARTICLE 14 - GENERAL PROVISIONS

14.1 Entire Agreement. This Agreement constitutes the entire agreement between the parties and supersedes all prior agreements, representations, and understandings.

14.2 Amendment. This Agreement may only be amended by a written instrument signed by authorized representatives of both parties.

14.3 Assignment. Neither party may assign this Agreement without the prior written consent of the other party, except in connection with a merger, acquisition, or sale of substantially all assets.

14.4 Notices. All notices shall be in writing and delivered by certified mail, overnight courier, or email with confirmation of receipt.

14.5 Severability. If any provision is held invalid, the remaining provisions shall continue in full force and effect.

14.6 No Third-Party Beneficiaries. This Agreement does not create any rights in any third party.

14.7 Counterparts. This Agreement may be executed in counterparts, each of which shall be deemed an original.

14.8 Survival. The following articles shall survive termination: Confidentiality, Intellectual Property, Indemnification, Liability, Governing Law, and all other provisions that by their nature should survive.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

{role1.upper()}: {c1[0]}
By: ____________________________
Name: {p1}
Title: {random.choice(['CEO', 'COO', 'SVP', 'Managing Director'])}
Date: {eff}

{role2.upper()}: {c2[0]}
By: ____________________________
Name: {p2}
Title: {random.choice(['VP of Operations', 'Director of Procurement', 'Chief Legal Officer'])}
Date: {eff}

"""
    return sections

# ── Contract type registry ──
CONTRACT_TYPES = [
    ("Software License", gen_software_license),
    ("NDA", gen_nda),
    ("Employment", gen_employment),
    ("SaaS Agreement", gen_saas_agreement),
    ("Vendor Agreement", gen_vendor),
    ("Procurement Contract", gen_procurement),
    ("Service Level Agreement", gen_sla),
    ("Professional Services", gen_professional),
    ("Consulting Agreement", gen_consulting),
    ("Partnership Agreement", gen_partnership),
    ("Joint Venture", gen_joint_venture),
    ("Franchise Agreement", gen_franchise),
    ("Real Estate Lease", gen_real_estate),
    ("Loan Agreement", gen_loan),
    ("Insurance Agreement", gen_insurance),
    ("Manufacturing Agreement", gen_manufacturing),
    ("Distribution Agreement", gen_distribution),
    ("Reseller Agreement", gen_reseller),
    ("Data Processing Agreement", gen_data_processing),
    ("Cloud Service Agreement", gen_cloud),
]

def build_pdf(output_path):
    """Build the massive legal contract repository PDF."""
    print(f"Generating Legal Contract Repository PDF...")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "ContractTitle", parent=styles["Heading1"],
        fontSize=16, spaceAfter=20, alignment=TA_CENTER,
        textColor=colors.HexColor("#1a1a2e"),
    ))
    styles.add(ParagraphStyle(
        "ContractBody", parent=styles["Normal"],
        fontSize=10, leading=14, alignment=TA_JUSTIFY,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "SectionHead", parent=styles["Heading2"],
        fontSize=12, spaceBefore=16, spaceAfter=8,
        textColor=colors.HexColor("#16213e"),
    ))
    styles.add(ParagraphStyle(
        "CoverTitle", parent=styles["Title"],
        fontSize=28, spaceAfter=30, alignment=TA_CENTER,
        textColor=colors.HexColor("#0f3460"),
    ))
    styles.add(ParagraphStyle(
        "CoverSub", parent=styles["Normal"],
        fontSize=14, alignment=TA_CENTER,
        textColor=colors.HexColor("#333333"),
    ))

    elements = []

    # Cover page
    elements.append(Spacer(1, 2 * inch))
    elements.append(Paragraph("LEGAL CONTRACT REPOSITORY", styles["CoverTitle"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Enterprise Contract Archive — Confidential", styles["CoverSub"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(HRFlowable(width="60%", color=colors.HexColor("#0f3460"), thickness=2))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles["CoverSub"]))
    elements.append(Paragraph("Contains 20 Contract Types | 40+ Individual Contracts", styles["CoverSub"]))
    elements.append(Paragraph("Classification: CONFIDENTIAL — For Internal Use Only", styles["CoverSub"]))
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Prepared by: Legal Operations Division", styles["CoverSub"]))
    elements.append(Paragraph("Document Control Number: LCR-2025-" + str(random.randint(10000, 99999)), styles["CoverSub"]))
    elements.append(PageBreak())

    # Table of Contents
    elements.append(Paragraph("TABLE OF CONTENTS", styles["ContractTitle"]))
    elements.append(Spacer(1, 0.3 * inch))
    
    contract_idx = 1
    toc_data = [["#", "Contract Type", "Parties"]]
    contracts_to_generate = []
    
    for type_name, gen_func in CONTRACT_TYPES:
        count = 3
        for _ in range(count):
            c1, c2 = rand_company_pair()
            toc_data.append([str(contract_idx), type_name, f"{c1[0][:25]}... / {c2[0][:25]}..."])
            contracts_to_generate.append((contract_idx, gen_func))
            contract_idx += 1
    
    toc_table = Table(toc_data, colWidths=[0.5*inch, 2.5*inch, 3.5*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f3460")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f5")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(toc_table)
    elements.append(PageBreak())

    # Generate contracts
    for idx, gen_func in contracts_to_generate:
        text = gen_func(idx)
        paragraphs = text.strip().split("\n\n")
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
            
            # Title detection
            if i == 0 or (para.isupper() and len(para) < 80):
                elements.append(Paragraph(para.replace("&", "&amp;"), styles["ContractTitle"] if i == 0 else styles["SectionHead"]))
            elif para.startswith("ARTICLE") or para.startswith("SECTION") or para.startswith("IN WITNESS"):
                elements.append(Paragraph(para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), styles["SectionHead"]))
            else:
                # Wrap long text
                safe = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                elements.append(Paragraph(safe, styles["ContractBody"]))
        
        elements.append(PageBreak())
        print(f"  Contract #{idx:04d} generated")

    print(f"Building PDF ({len(contracts_to_generate)} contracts)...")
    doc.build(elements)
    
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n[OK] PDF generated successfully!")
    print(f"   Path: {output_path}")
    print(f"   Size: {size_mb:.1f} MB")
    print(f"   Contracts: {len(contracts_to_generate)}")

if __name__ == "__main__":
    output = os.path.join(os.path.dirname(__file__), "Legal_Contract_Repository_2025.pdf")
    build_pdf(output)
