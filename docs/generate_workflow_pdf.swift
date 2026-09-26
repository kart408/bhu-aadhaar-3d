import AppKit
import CoreGraphics

let output = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Bhu-Aadhaar-3D-End-to-End-Workflow.pdf"
let page = CGRect(x: 0, y: 0, width: 595, height: 842)
let margin: CGFloat = 48

let navy = NSColor(calibratedRed: 0.055, green: 0.10, blue: 0.18, alpha: 1)
let teal = NSColor(calibratedRed: 0.02, green: 0.55, blue: 0.55, alpha: 1)
let cyan = NSColor(calibratedRed: 0.10, green: 0.78, blue: 0.82, alpha: 1)
let ink = NSColor(calibratedWhite: 0.12, alpha: 1)
let slate = NSColor(calibratedWhite: 0.36, alpha: 1)
let mist = NSColor(calibratedRed: 0.94, green: 0.97, blue: 0.98, alpha: 1)
let amber = NSColor(calibratedRed: 0.93, green: 0.55, blue: 0.12, alpha: 1)
let red = NSColor(calibratedRed: 0.76, green: 0.18, blue: 0.18, alpha: 1)

func font(_ size: CGFloat, _ weight: NSFont.Weight = .regular, mono: Bool = false) -> NSFont {
    if mono { return NSFont.monospacedSystemFont(ofSize: size, weight: weight) }
    return NSFont.systemFont(ofSize: size, weight: weight)
}

final class PDFDoc {
    let ctx: CGContext
    var pageNo = 0
    var y: CGFloat = margin
    var graphics: NSGraphicsContext?

    init(path: String) {
        let url = URL(fileURLWithPath: path) as CFURL
        var box = page
        guard let consumer = CGDataConsumer(url: url),
              let context = CGContext(consumer: consumer, mediaBox: &box, nil) else { fatalError("Could not create PDF") }
        ctx = context
    }

    func begin(_ section: String? = nil) {
        pageNo += 1
        ctx.beginPDFPage(nil)
        ctx.saveGState()
        ctx.translateBy(x: 0, y: page.height)
        ctx.scaleBy(x: 1, y: -1)
        graphics = NSGraphicsContext(cgContext: ctx, flipped: true)
        NSGraphicsContext.current = graphics
        NSColor.white.setFill(); NSBezierPath(rect: page).fill()
        y = margin
        if pageNo > 1 {
            fill(CGRect(x: 0, y: 0, width: page.width, height: 8), teal)
            text("BHU-AADHAAR 3D  /  TECHNICAL WORKFLOW", x: margin, y: 24, w: 360, size: 8, color: slate, weight: .semibold)
            if let section { text(section.uppercased(), x: 390, y: 24, w: 157, size: 8, color: teal, weight: .semibold, align: .right) }
            y = 55
        }
    }

    func end() {
        if pageNo > 1 {
            line(x1: margin, y1: 802, x2: page.width-margin, y2: 802, color: NSColor(calibratedWhite: 0.86, alpha: 1))
            text("Prototype v0.1 · Synthetic demo · Not an official DoLR standard", x: margin, y: 812, w: 400, size: 8, color: slate)
            text("\(pageNo)", x: 500, y: 812, w: 47, size: 8, color: slate, align: .right)
        }
        NSGraphicsContext.current = nil
        ctx.restoreGState(); ctx.endPDFPage()
    }

    func finish() { ctx.closePDF() }

    @discardableResult func text(_ value: String, x: CGFloat? = nil, y yy: CGFloat? = nil, w: CGFloat? = nil,
                                size: CGFloat = 10.5, color: NSColor = ink, weight: NSFont.Weight = .regular,
                                mono: Bool = false, align: NSTextAlignment = .left, leading: CGFloat = 1.25) -> CGFloat {
        let px = x ?? margin, py = yy ?? y, width = w ?? (page.width - margin*2)
        let para = NSMutableParagraphStyle(); para.alignment = align; para.lineBreakMode = .byWordWrapping
        para.minimumLineHeight = size * leading; para.maximumLineHeight = size * leading
        let attrs: [NSAttributedString.Key: Any] = [.font: font(size, weight, mono: mono), .foregroundColor: color, .paragraphStyle: para]
        let rect = (value as NSString).boundingRect(with: NSSize(width: width, height: 2000), options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: attrs)
        (value as NSString).draw(with: CGRect(x: px, y: py, width: width, height: ceil(rect.height)+3), options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: attrs)
        if yy == nil { y = py + ceil(rect.height) + 3 }
        return ceil(rect.height) + 3
    }

    func title(_ value: String, subtitle: String? = nil) {
        text(value, size: 25, color: navy, weight: .bold, leading: 1.08)
        if let subtitle { y += 6; text(subtitle, size: 11.5, color: slate, leading: 1.35) }
        y += 16
    }

    func h2(_ value: String) { y += 7; text(value, size: 15, color: navy, weight: .bold); y += 5 }
    func p(_ value: String) { text(value, size: 10.4, color: ink, leading: 1.38); y += 7 }
    func bullet(_ value: String, color: NSColor = teal) {
        fill(CGRect(x: margin+2, y: y+5, width: 5, height: 5), color)
        text(value, x: margin+16, y: y, w: page.width-margin*2-16, size: 10.1, color: ink, leading: 1.34)
        y += 4
    }
    func code(_ value: String) {
        let h = measure(value, width: page.width-margin*2-22, size: 9, mono: true, leading: 1.35) + 18
        roundRect(CGRect(x: margin, y: y, width: page.width-margin*2, height: h), radius: 6, fill: navy)
        text(value, x: margin+11, y: y+9, w: page.width-margin*2-22, size: 9, color: NSColor.white, mono: true, leading: 1.35)
        y += h + 10
    }
    func callout(_ heading: String, _ body: String, tone: NSColor = teal) {
        let h = max(56, measure(body, width: page.width-margin*2-40, size: 9.7, leading: 1.34) + 35)
        roundRect(CGRect(x: margin, y: y, width: page.width-margin*2, height: h), radius: 7, fill: mist)
        fill(CGRect(x: margin, y: y, width: 5, height: h), tone)
        text(heading.uppercased(), x: margin+16, y: y+10, w: 450, size: 8, color: tone, weight: .bold)
        text(body, x: margin+16, y: y+25, w: page.width-margin*2-32, size: 9.7, color: ink, leading: 1.34)
        y += h + 10
    }
    func box(_ heading: String, _ body: String, x: CGFloat, yy: CGFloat, w: CGFloat, h: CGFloat, accent: NSColor = teal) {
        roundRect(CGRect(x: x, y: yy, width: w, height: h), radius: 8, fill: NSColor.white, stroke: NSColor(calibratedWhite: 0.84, alpha: 1))
        fill(CGRect(x: x, y: yy, width: w, height: 6), accent)
        text(heading, x: x+12, y: yy+15, w: w-24, size: 11, color: navy, weight: .bold)
        text(body, x: x+12, y: yy+37, w: w-24, size: 8.8, color: slate, leading: 1.3)
    }
    func step(_ n: Int, _ heading: String, _ body: String) {
        fillEllipse(CGRect(x: margin, y: y, width: 28, height: 28), teal)
        text("\(n)", x: margin, y: y+5, w: 28, size: 10, color: .white, weight: .bold, align: .center)
        text(heading, x: margin+42, y: y, w: 455, size: 11, color: navy, weight: .bold)
        let bh = text(body, x: margin+42, y: y+18, w: 455, size: 9.5, color: slate, leading: 1.32)
        y += max(43, bh+23) + 5
    }
    func measure(_ value: String, width: CGFloat, size: CGFloat, mono: Bool = false, leading: CGFloat = 1.25) -> CGFloat {
        let para = NSMutableParagraphStyle(); para.minimumLineHeight = size*leading; para.maximumLineHeight = size*leading
        let attrs: [NSAttributedString.Key: Any] = [.font: font(size, .regular, mono: mono), .paragraphStyle: para]
        return ceil((value as NSString).boundingRect(with: NSSize(width: width, height: 2000), options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: attrs).height)
    }
    func fill(_ rect: CGRect, _ color: NSColor) { color.setFill(); NSBezierPath(rect: rect).fill() }
    func fillEllipse(_ rect: CGRect, _ color: NSColor) { color.setFill(); NSBezierPath(ovalIn: rect).fill() }
    func roundRect(_ rect: CGRect, radius: CGFloat, fill: NSColor, stroke: NSColor? = nil) {
        let p = NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius); fill.setFill(); p.fill()
        if let stroke { stroke.setStroke(); p.lineWidth = 1; p.stroke() }
    }
    func line(x1: CGFloat, y1: CGFloat, x2: CGFloat, y2: CGFloat, color: NSColor = teal, width: CGFloat = 1) {
        let p=NSBezierPath(); p.move(to:NSPoint(x:x1,y:y1)); p.line(to:NSPoint(x:x2,y:y2)); color.setStroke(); p.lineWidth=width; p.stroke()
    }
}

let d = PDFDoc(path: output)

// Cover
d.begin()
d.fill(CGRect(x: 0, y: 0, width: page.width, height: page.height), navy)
d.fill(CGRect(x: 0, y: 0, width: 12, height: page.height), teal)
d.text("TECHNICAL WORKFLOW", x: 55, y: 76, w: 460, size: 10, color: cyan, weight: .bold)
d.text("Bhu-Aadhaar 3D", x: 55, y: 116, w: 485, size: 34, color: .white, weight: .bold, leading: 1.0)
d.text("Complete 3D Visualization\nProject Handbook", x: 55, y: 166, w: 485, size: 24, color: NSColor(calibratedWhite: 0.91, alpha: 1), weight: .medium, leading: 1.2)
d.roundRect(CGRect(x: 55, y: 290, width: 485, height: 236), radius: 14, fill: NSColor(calibratedRed: 0.08, green: 0.15, blue: 0.25, alpha: 1))
let coverItems = [
    ("01", "Capture", "Manual measurements or synthetic LiDAR point cloud"),
    ("02", "Model", "Metric 3D box, deterministic locator and proposal"),
    ("03", "Validate", "Parcel containment, 3D overlap and record consistency"),
    ("04", "Register", "Officer decision, SQLite persistence and audit chain"),
    ("05", "Verify", "Signed QR credential and offline Web Crypto validation")
]
for (i,item) in coverItems.enumerated() {
    let yy = 312 + CGFloat(i)*41
    d.text(item.0, x: 75, y: yy, w: 34, size: 9, color: cyan, weight: .bold)
    d.text(item.1, x: 118, y: yy-1, w: 83, size: 11, color: .white, weight: .semibold)
    d.text(item.2, x: 205, y: yy, w: 310, size: 9.2, color: NSColor(calibratedWhite: 0.78, alpha: 1))
}
d.text("PROJECT STATUS", x: 55, y: 606, w: 150, size: 8, color: cyan, weight: .bold)
d.text("Hackathon prototype · Phases 1–16 implemented", x: 55, y: 625, w: 485, size: 12, color: .white, weight: .medium)
d.text("Prepared from the repository implementation on 26 September 2026", x: 55, y: 650, w: 485, size: 9.5, color: NSColor(calibratedWhite: 0.65, alpha: 1))
d.text("Important: experimental synthetic demonstration; not a legal cadastral system or official DoLR identifier standard.", x: 55, y: 744, w: 485, size: 9, color: NSColor(calibratedRed: 1, green: 0.72, blue: 0.35, alpha: 1), weight: .semibold, leading: 1.35)
d.end()

// Contents
d.begin("Contents")
d.title("Document map", subtitle: "A complete guide to the idea, visualization, algorithms, applications and deployment path")
let toc = [
    ("01", "System at a glance", "Purpose, users and the complete lifecycle"),
    ("02", "Algorithms used", "3D identifier, geometry and collision checks"),
    ("03", "Survey + reconciliation", "Point-cloud detection and record rules"),
    ("04", "Operational workflow", "Intake through approval and verification"),
    ("05", "Technology stack", "Frontend, backend, storage and cryptography"),
    ("06", "Components + data flow", "Applications, REST API and database"),
    ("07", "Integrity + security", "Audit chain and signed QR credentials"),
    ("08", "Validation + operation", "Tests, setup and known limitations"),
    ("09", "3D visualization", "Coordinate model, projection and interaction"),
    ("10", "Application guide", "What each of the five browser apps does"),
    ("11", "Demo scenarios", "Tower, parking, utility and rejected proposals"),
    ("12", "Contracts + schemas", "Identifier, proposal, GeoJSON and API"),
    ("13", "Production roadmap", "From proof of concept to cadastral platform"),
    ("14", "Glossary + repository map", "Terms and important source files")
]
for (i,item) in toc.enumerated() {
    let col = i < 7 ? 0 : 1
    let row = col == 0 ? i : i-7
    let x = margin + CGFloat(col)*255
    let yy = d.y + CGFloat(row)*84
    d.text(item.0, x: x, y: yy, w: 34, size: 10, color: teal, weight: .bold)
    d.text(item.1, x: x+42, y: yy-2, w: 198, size: 11, color: navy, weight: .bold)
    d.text(item.2, x: x+42, y: yy+19, w: 198, size: 8.8, color: slate, leading: 1.32)
    d.line(x1: x+42, y1: yy+59, x2: x+237, y2: yy+59, color: NSColor(calibratedWhite: 0.9, alpha: 1))
}
d.y += 608
d.callout("Reading paths", "For a quick presentation, read sections 1, 4, 9 and 11. For implementation, focus on 2, 3, 5, 6 and 12. For governance and deployment decisions, use sections 7, 8 and 13.")
d.end()

// Executive overview
d.begin("Overview")
d.title("1. System at a glance", subtitle: "What the prototype does, from property input to public verification")
d.callout("Purpose", "The system derives a compact 3D locator beneath an existing 14-digit ULPIN, stores the exact legal-style geometry separately, checks for obvious spatial and record conflicts, records an auditable registrar decision, and exposes privacy-safe 3D and citizen-verification views.")
d.h2("End-to-end pipeline")
let bw: CGFloat = 91, gap: CGFloat = 11, by = d.y
let stages = [("CAPTURE","Form / point cloud"),("GEOMETRY","XYZ bounds"),("VALIDATE","Inside / overlap"),("REGISTER","SQLite + audit"),("VERIFY","3D / signed QR")]
for (i,s) in stages.enumerated() {
    let x = margin + CGFloat(i)*(bw+gap)
    d.box(s.0, s.1, x: x, yy: by, w: bw, h: 78, accent: i == 4 ? amber : teal)
    if i < stages.count-1 { d.text("→", x: x+bw, y: by+29, w: gap, size: 13, color: teal, weight: .bold, align: .center) }
}
d.y = by + 99
d.h2("Design principle: code is not geometry")
d.p("The 23-character ULPIN-3D code is a compact, deterministic locator. It contains a parent ULPIN, relative centroid, floor level, height and checksum. The authoritative shape, coordinate reference system (CRS), height datum, provenance, rights and decisions remain registry records. This separation prevents a short identifier from pretending to be a legal boundary.")
d.h2("Primary users")
d.bullet("Citizen / applicant — enters property details, imports a demo scan, reviews the generated box and submits a proposal.")
d.bullet("Registrar — reviews the proposal and advisory spatial result, then approves or rejects; any approval that bypasses a spatial failure needs an explicit waiver reason.")
d.bullet("Public viewer — looks up a parent ULPIN and sees geometry and registration facts without applicant identity.")
d.bullet("Citizen verifier — scans or pastes a signed credential and validates it locally against cached issuer keys.")
d.callout("Trust boundary", "A ULPIN lookup is not authentication. Public output excludes owner/applicant identity. Spatial checks and automated reconciliation are advisory; authorized human review remains necessary.", tone: amber)
d.end()

// Algorithms
d.begin("Algorithms")
d.title("2. Algorithms used", subtitle: "Deterministic logic implemented in Python and browser JavaScript")
d.h2("A. ULPIN-3D compact encoding")
d.p("Format: 14 parent digits + 4 horizontal Base32 characters + 4 vertical Base32 characters + 1 check character. Hyphens are display-only.")
d.code("PPPPPPPPPPPPPP-HHHH-ZZZZ-C\nExample stored length: 23 characters (without hyphens)")
d.bullet("Quantize easting and northing offsets from the parcel centroid to 0.5 m using round-half-away-from-zero.")
d.bullet("Represent each offset as signed 10-bit two’s-complement; interleave their bits (Morton/Z-order style) into 20 bits.")
d.bullet("Encode floor as signed 10-bit units and volume height as unsigned 10-bit units; concatenate to another 20 bits.")
d.bullet("Encode both 20-bit fields with Crockford Base32 and append a generalized Luhn mod-32 checksum.")
d.callout("Representable ranges", "Horizontal and floor offsets: −256.0 m to +255.5 m. Height: 0.5 m to 511.5 m. Decoding recovers a coarse locator, not the exact footprint.")
d.h2("B. Geometry and collision validation")
d.p("Every property is an axis-aligned rectangular prism represented as [xMin, yMin, xMax, yMax, zMin, zMax]. Dimensions must have positive extent. Area = (xMax−xMin)(yMax−yMin); volume = area(zMax−zMin).")
d.code("3D intersection ⇔\nmax(x₁min,x₂min) < min(x₁max,x₂max)  AND\nmax(y₁min,y₂min) < min(y₁max,y₂max)  AND\nmax(z₁min,z₂min) < min(z₁max,z₂max)")
d.p("Strict inequalities mean face-touching volumes are allowed. Parcel containment checks X/Y limits; the current prototype parcel bounds are a fixed demo envelope.")
d.end()

// Point cloud and reconciliation
d.begin("Algorithms")
d.title("3. Survey detection and reconciliation", subtitle: "How scan samples and administrative records become actionable findings")
d.h2("Point-cloud floor / ceiling detector")
d.step(1, "Validate samples", "Require at least 24 finite [x,y,z] points by default (12 samples for each candidate surface).")
d.step(2, "Cluster by elevation", "Sort points by Z. Add a point to the current cluster when it is within 0.08 m of the running cluster mean; otherwise start a new cluster.")
d.step(3, "Keep strong surfaces", "Retain clusters with at least 12 samples and sort their mean elevations from low to high.")
d.step(4, "Choose a plausible room band", "Among adjacent surfaces 2–6 m apart, select the pair with the greatest combined sample count. These become floor and ceiling.")
d.step(5, "Construct the survey box", "Use global min/max X and Y plus the selected Z means. Confidence = selected floor and ceiling samples ÷ all points, capped at 1.0.")
d.callout("Scope", "This is a transparent heuristic for a synthetic point cloud, not a production LiDAR segmentation pipeline. It does not estimate tilted planes, remove outliers, register scans, or quantify legal survey uncertainty.", tone: amber)
d.h2("Administrative reconciliation rules")
d.bullet("SHARE_TOTAL (HIGH): sum of undivided shares must equal 100.00% within 0.01 percentage points.")
d.bullet("AREA_MISMATCH (MEDIUM): declared carpet area may differ from mapped footprint by at most 5%.")
d.bullet("DUPLICATE_ACTIVE_RIGHT (CRITICAL): more than one active exclusive ownership claim references the same volume.")
d.bullet("MISSING_GEOMETRY (HIGH): a unit record has no corresponding registered geometry.")
d.p("Findings are sorted by severity and reported as CLEAR or FLAGGED. The engine explicitly does not decide ownership.")
d.end()

// Workflow detailed
d.begin("Workflow")
d.title("4. End-to-end operational workflow", subtitle: "The exact journey through the current applications and backend")
d.step(1, "Open intake application", "The applicant enters owner label, property type, address, unit, 14-digit ULPIN, floor and dimensions. Input validation requires non-empty labels, a valid ULPIN and positive measurements.")
d.step(2, "Select geometry source", "Manual mode converts feet to metres and places an axis-aligned box. Survey mode loads the 136-point synthetic scan and derives its floor, ceiling and envelope using the detector.")
d.step(3, "Resolve demo placement", "Known demo units use a small directory. Unknown address/unit pairs use FNV-1a-style stable hashing to produce repeatable offline coordinates; this is clearly labeled as demo placement, not geocoding.")
d.step(4, "Create deterministic proposal", "The browser hashes ULPIN | uppercased unit | bounds with SHA-256, uses the first 6 digest bytes, and creates {ULPIN}-P3D-{12 hex}. A BHU3D_PROPERTY_PROPOSAL_V1 JSON payload includes XYZ bounds, source and provenance.")
d.step(5, "Submit and validate server-side", "POST /api/proposals validates schema and fields, checks X/Y parcel containment and positive-volume intersection against registered volumes, then stores the proposal as PENDING_REVIEW.")
d.step(6, "Registrar decision", "The officer records APPROVED or REJECTED. Approval after failed spatial validation requires a written geometry waiver; the decision and waiver status are retained in the audit history.")
d.step(7, "Persist registration atomically", "Approved property snapshot, proposal status and audit events are committed in one SQLite transaction. The registration records bounds, provenance, approval identity/time and basis.")
d.step(8, "Publish and verify", "The ULPIN viewer merges approved records into the parcel model. Separately, an ES256-signed QR envelope can be checked in the offline-capable verifier for issuer trust, revocation, integrity, canonical JSON and expiry.")
d.end()

// Technology
d.begin("Technology")
d.title("5. Technology stack", subtitle: "Small, dependency-light components with clear responsibilities")
let techY = d.y
d.box("Browser UI", "HTML5 · CSS3 · native ES modules · Fetch · Web Crypto · BarcodeDetector · Service Worker", x: margin, yy: techY, w: 240, h: 107, accent: teal)
d.box("3D rendering", "Canvas/SVG-style dependency-free project viewer driven by GeoJSON footprints and local XYZ bounds", x: 307, yy: techY, w: 240, h: 107, accent: cyan)
d.box("Backend", "Python 3 standard library · ThreadingHTTPServer · JSON REST handlers · deterministic domain packages", x: margin, yy: techY+122, w: 240, h: 107, accent: amber)
d.box("Persistence", "SQLite · proposal, registered_properties and append-only audit_events tables · transactional writes", x: 307, yy: techY+122, w: 240, h: 107, accent: teal)
d.box("Spatial exchange", "GeoJSON FeatureCollection · WGS84 visualization anchor · metric local bounds for validation", x: margin, yy: techY+244, w: 240, h: 107, accent: cyan)
d.box("Cryptography", "SHA-256 · ES256 / ECDSA P-256 · canonical JSON · Base64URL · cached JWK trust store", x: 307, yy: techY+244, w: 240, h: 107, accent: amber)
d.y = techY + 374
d.h2("Runtime dependencies")
d.bullet("Python packages: cryptography 46.x for P-256 signing; qrcode 8.x for credential QR generation.")
d.bullet("No JavaScript framework, build system or database server is required. package.json only selects ES module semantics.")
d.h2("Data artifacts")
d.bullet("Seed JSON: synthetic tower and property records. Generated artifacts: GeoJSON volumes, reports, point cloud, signed citizen payload and SQLite registry.")
d.callout("Coordinate note", "Local metre coordinates drive box math. Conversion to longitude/latitude is approximate and visualization-only (111,320 m/degree latitude and an adjusted longitude factor near the demo latitude).", tone: amber)
d.end()

// Data flow architecture
d.begin("Architecture")
d.title("6. Components and data flow", subtitle: "Where information is produced, checked, stored and exposed")
let ay = d.y
d.box("INTAKE", "geometry.js\npointcloud.js\nproposal-transfer.js", x: 48, yy: ay, w: 143, h: 102, accent: teal)
d.box("REGISTRY API", "run_registry_server.py\nProposalRegistry\nserver-side validation", x: 226, yy: ay, w: 143, h: 102, accent: amber)
d.box("SQLITE", "proposals\nregistered_properties\naudit_events", x: 404, yy: ay, w: 143, h: 102, accent: cyan)
d.text("POST proposal  →", x: 185, y: ay+39, w: 47, size: 8, color: teal, weight: .bold, align: .center)
d.text("transaction  →", x: 365, y: ay+39, w: 43, size: 8, color: teal, weight: .bold, align: .center)
d.line(x1: 475, y1: ay+110, x2: 475, y2: ay+162, color: teal, width: 1.5)
d.text("approved model", x: 430, y: ay+125, w: 90, size: 8, color: teal, weight: .bold, align: .center)
d.box("PUBLIC VIEWER", "ULPIN-isolated GeoJSON\nNo applicant identity\nOptional scan overlay", x: 315, yy: ay+165, w: 190, h: 105, accent: teal)
d.box("REGISTRAR", "review proposal\napprove / reject\nwaiver if required", x: 90, yy: ay+165, w: 190, h: 105, accent: amber)
d.line(x1: 297, y1: ay+102, x2: 190, y2: ay+165, color: amber, width: 1.5)
d.text("GET + decision", x: 190, y: ay+126, w: 96, size: 8, color: amber, weight: .bold, align: .center)
d.y = ay + 295
d.h2("HTTP interface")
d.code("POST /api/proposals\nGET  /api/proposals/{proposal_id}\nPOST /api/proposals/{proposal_id}/decision\nGET  /api/proposals/{proposal_id}/audit\nGET  /api/parcels/{14_digit_ulpin}/model")
d.h2("Core registry records")
d.bullet("Proposal: schema, proposal ID, parent ULPIN, applicant label, property/unit/address, bounds, geometry source and provenance.")
d.bullet("Validation: accepted flag, intersecting volume keys and error codes.")
d.bullet("Registration: approved geometry snapshot, source/provenance, registration basis, approval time and officer.")
d.bullet("Audit event: global sequence, proposal, type, canonical detail JSON, UTC timestamp, previous hash and event hash.")
d.end()

// Security verification
d.begin("Integrity")
d.title("7. Integrity, security and offline verification", subtitle: "What is protected—and what is deliberately outside prototype scope")
d.h2("Tamper-evident audit chain")
d.p("Each event links to the prior event’s SHA-256 digest. The material uses a unit-separator delimiter to avoid ambiguous concatenation:")
d.code("eventHash = SHA256(previousHash ␟ proposalId ␟ eventType\n                   ␟ canonicalDetailJson ␟ occurredAt)")
d.p("Verification walks events in sequence, recomputes every digest and confirms both the previous-hash pointer and event hash. This detects stored-event modification, but it is not a blockchain, external timestamp, append-only storage guarantee or protection against an attacker who can rewrite the entire database and all hashes.")
d.h2("Signed citizen credential")
d.step(1, "Canonicalize", "Serialize payload JSON with sorted keys and compact separators.")
d.step(2, "Sign", "Issuer signs the raw canonical bytes using ECDSA P-256 with SHA-256 (ES256). Signature is stored as 64-byte r || s.")
d.step(3, "Envelope", "BHU3D2.{base64url payload}.{key ID}.{base64url signature}; a QR code transports the envelope.")
d.step(4, "Verify offline", "Browser selects a cached JWK by key ID, rejects revoked/unknown keys, verifies the signature using Web Crypto, checks canonical form and requires SYNTHETIC_DEMO status.")
d.step(5, "Check validity", "Credential expiration is compared with the device clock before property facts are displayed.")
d.callout("Production requirements", "Add authenticated roles, secure key custody/HSM, online revocation freshness, TLS, authorization on owner data, database access controls, backups, external audit anchoring, rate limiting and a formal threat model.", tone: red)
d.end()

// limitations and test/run
d.begin("Operate")
d.title("8. Validation, limitations and how to run", subtitle: "Engineering evidence and the boundary between demonstration and deployment")
d.h2("Automated test coverage")
d.bullet("Python: ULPIN codec round-trip/checksum/ranges, geometry containment and overlap, reconciliation, registry transactions/audit, signed payload verification.")
d.bullet("JavaScript: intake geometry, point-cloud detection, registrar validation and proposal transfer.")
d.code("python3 -m unittest discover -s tests -v\nnode --test tests/*.mjs")
d.h2("Build and start")
d.code("python3 scripts/build_demo.py\npython3 scripts/reconcile_demo.py\npython3 scripts/build_pointcloud_demo.py\npython3 -m venv .venv\n.venv/bin/pip install -r requirements.txt\n.venv/bin/python scripts/build_citizen_payload.py\n.venv/bin/python scripts/run_registry_server.py")
d.p("Then open http://127.0.0.1:8000/apps/intake/ . The viewer, registrar, reconciliation and verifier applications are sibling paths under /apps/.")
d.h2("Known limitations")
d.bullet("Rectangular, axis-aligned volumes only; no arbitrary polygons/polyhedra, tilted structures or topology model.", color: amber)
d.bullet("Fixed demo parcel bounds and approximate visualization conversion; no production CRS transformation or vertical datum service.", color: amber)
d.bullet("Synthetic point cloud and deterministic offline placement; neither proves a surveyed real-world location.", color: amber)
d.bullet("Prototype code version is registry metadata, not embedded in the identifier. The spec requires explicit versioning before deployment.", color: amber)
d.bullet("Administrative approval can waive spatial findings when a reason is recorded; this is for demonstration and is unsafe as a normal cadastral policy.", color: amber)
d.callout("Bottom line", "The prototype successfully demonstrates a traceable technical chain from property capture to a registered 3D visualization and cryptographically verifiable citizen credential. It should be treated as an explainable proof of concept—not as legal title infrastructure.", tone: teal)
d.end()

// 3D visualization deep dive
d.begin("Visualization")
d.title("9. How the 3D visualization works", subtitle: "From six coordinates to an explorable building model")
d.h2("The spatial model")
d.p("The renderer receives one GeoJSON feature per volumetric object. The polygon footprint provides the map anchor; properties carry base height, top height and local six-coordinate bounds. Each object is treated as a rectangular prism and projected into a 2D canvas using an isometric view.")
let vy = d.y
d.box("LOCAL X", "Left ↔ right within the parcel or building plan, measured in metres.", x: margin, yy: vy, w: 153, h: 92, accent: teal)
d.box("LOCAL Y", "Front ↔ back within the local metric coordinate frame.", x: 221, yy: vy, w: 153, h: 92, accent: cyan)
d.box("RELATIVE Z", "Below ground, ground and floor height relative to the demo building datum.", x: 394, yy: vy, w: 153, h: 92, accent: amber)
d.y = vy + 112
d.h2("Volume-to-screen pipeline")
d.step(1, "Load a ULPIN-isolated model", "GET /api/parcels/{ulpin}/model returns only features assigned to that parent identifier, including approved registrations merged at request time.")
d.step(2, "Normalize model extents", "The renderer establishes the local bounding range so apartments, parking spaces, utility volumes and rejected proposals share one view.")
d.step(3, "Project corners", "Eight prism corners are transformed from local XYZ into isometric screen coordinates. Visible faces form the displayed box; height remains visually distinguishable.")
d.step(4, "Apply semantic styling", "Registered units use category/floor colors. Underground and basement volumes remain distinct. Rejected conflicts are red so validation state is visible spatially.")
d.step(5, "Add interaction", "Filters control type and floor. Clicking a volume reveals its 3D identifier, registration state, elevation band, area, volume and validation findings.")
d.h2("LiDAR overlay")
d.p("The 136 synthetic scan points use the same local XYZ frame as the generated Shop G-12 volume. Toggling the overlay displays evidence and derived geometry together, making the floor/ceiling inference understandable instead of opaque.")
d.callout("Visualization truth", "The display is a communication layer. Pixel position, camera perspective and approximate map conversion are not cadastral measurements. Metric bounds and provenance in the registry remain the operative data.", tone: amber)
d.end()

// Application guide
d.begin("Applications")
d.title("10. Application-by-application guide", subtitle: "Five focused interfaces built on one shared proposal and geometry model")
let appY = d.y
d.box("PROPERTY INTAKE", "/apps/intake/\nCollect property details; create geometry manually or from the demo scan; preview and submit a proposal.", x: margin, yy: appY, w: 240, h: 116, accent: teal)
d.box("REGISTRAR", "/apps/registrar/\nLoad the pending proposal; review essential fields and validation; record an audited administrative decision.", x: 307, yy: appY, w: 240, h: 116, accent: amber)
d.box("3D VIEWER", "/apps/viewer/\nLook up one parent ULPIN; explore registered and rejected volumes; filter floors and display LiDAR points.", x: margin, yy: appY+132, w: 240, h: 116, accent: cyan)
d.box("RECONCILIATION", "/apps/reconcile/\nPresent share, area and duplicate-right consistency findings with severity and evidence.", x: 307, yy: appY+132, w: 240, h: 116, accent: red)
d.box("CITIZEN VERIFY", "/apps/verify/\nScan or paste a BHU3D2 credential; validate issuer signature, revocation, canonical form and expiry offline.", x: 176, yy: appY+264, w: 240, h: 116, accent: teal)
d.y = appY + 403
d.h2("What connects them")
d.bullet("A single proposal contract allows both owner-entered and scan-derived geometry to follow the same registrar workflow.")
d.bullet("A shared parent ULPIN partitions the data shown by the viewer and associates every child volume with a parcel.")
d.bullet("The backend repeats validation and persists decisions; browser checks improve usability but are never the trust boundary.")
d.bullet("Privacy-safe model output separates public geometry facts from applicant identity and protected records.")
d.callout("Fallback mode", "When the durable registry API is unavailable and the project is served statically, intake can use same-origin localStorage to demonstrate handoff. This is a convenience fallback, not a production submission channel.", tone: amber)
d.end()

// Demo scenarios
d.begin("Demo model")
d.title("11. Synthetic tower and demonstration scenarios", subtitle: "What is present in the model and what each case is designed to prove")
d.h2("Registered 3D content")
let sy = d.y
d.box("8 APARTMENTS", "Four floors × two units. Adjacent boxes may share walls or slabs without being classified as overlap.", x: margin, yy: sy, w: 153, h: 105, accent: teal)
d.box("2 PARKING VOLUMES", "Basement spaces demonstrate that independent property volumes can exist below ground level.", x: 221, yy: sy, w: 153, h: 105, accent: cyan)
d.box("1 UTILITY VOLUME", "An underground service space demonstrates non-residential volumetric rights or restrictions.", x: 394, yy: sy, w: 153, h: 105, accent: amber)
d.y = sy + 126
d.h2("Deliberate validation cases")
d.step(1, "Clean upper-floor proposal", "Fits inside the parcel and occupies unused XYZ space. It illustrates a normal positive validation path.")
d.step(2, "Duplicate of Unit 302", "Occupies the same positive 3D volume as a registered unit and must be reported as a spatial conflict.")
d.step(3, "Outside-parent proposal", "Its horizontal bounds cross the parcel envelope and generate OUTSIDE_PARENT_PARCEL.")
d.step(4, "Shop G-12 scan proposal", "The synthetic scan produces a proposal that overlaps registered ground-floor geometry. A 12 ft owner-entered height can also cross a 3.0 m storey boundary, explaining multiple conflicts.")
d.h2("Reconciliation findings planted in the data")
d.bullet("Undivided shares total 103%, not 100%.", color: red)
d.bullet("Unit 401 declared area differs from mapped area by 20%.", color: amber)
d.bullet("Unit 302 has two active ownership deed claims.", color: red)
d.callout("Why synthetic exceptions matter", "A convincing visualization should show failure states, not only a perfect building. These planted cases demonstrate that the system can explain boundary errors, volume conflicts and administrative inconsistency to reviewers.")
d.end()

// Contracts
d.begin("Contracts")
d.title("12. Identifiers, payloads and API contracts", subtitle: "The machine-readable agreements that keep all modules interoperable")
d.h2("Identifier")
d.code("12345678901234-HHHH-ZZZZ-C\nparent parcel   horizontal  vertical  checksum")
d.h2("Proposal JSON — BHU3D_PROPERTY_PROPOSAL_V1")
d.code("{\n  \"schema\": \"BHU3D_PROPERTY_PROPOSAL_V1\",\n  \"id\": \"12345678901234-P3D-ABCDEF123456\",\n  \"parent_ulpin\": \"12345678901234\",\n  \"applicant\": \"Applicant label\",\n  \"property_type\": \"Shop\", \"unit\": \"G-12\",\n  \"address\": \"ABC Complex, Hyderabad\",\n  \"bounds_m\": [x1, y1, x2, y2, z1, z2],\n  \"geometry_source\": \"SYNTHETIC_POINT_CLOUD\",\n  \"provenance\": { \"accuracy_m\": 0.05, \"point_count\": 136 }\n}")
d.h2("GeoJSON feature properties")
d.p("Each visualization feature exposes key, kind, ULPIN-3D, base/top/height, footprint area, volume, local bounds, synthetic-data status and registration status. Approved API-created features also carry geometry source, registration basis and approval time.")
d.h2("Status lifecycle")
d.code("SUBMITTED → PENDING_REVIEW → APPROVED → REGISTERED\n                           └──────→ REJECTED")
d.callout("Important distinction", "A proposal ID is a deterministic workflow reference; it is not the compact ULPIN-3D code. Registration records exact geometry. A signed citizen envelope transports a verified snapshot. These artifacts serve different purposes.", tone: amber)
d.end()

// Production roadmap
d.begin("Roadmap")
d.title("13. Production evolution roadmap", subtitle: "A practical sequence for turning the demonstrator into governed infrastructure")
d.h2("Phase A — Geospatial correctness")
d.bullet("Adopt authoritative projected and vertical coordinate reference systems, transformation grids and explicit datum metadata.")
d.bullet("Replace boxes with valid 2.5D/3D solids, topology checks, tolerances and an OGC-aligned representation such as CityGML/IndoorGML where appropriate.")
d.bullet("Use PostGIS or a dedicated spatial engine for indexing, containment, volumetric intersection and parcel-scale queries.")
d.h2("Phase B — Survey and BIM integration")
d.bullet("Ingest LAS/LAZ/E57 and IFC sources; run registration, noise removal, plane segmentation, wall extraction and quality scoring through PDAL/Open3D/BIM tooling.")
d.bullet("Require licensed survey provenance, accuracy class, equipment, acquisition time, transformation report and reviewer attestation.")
d.h2("Phase C — Secure registry platform")
d.bullet("Add identity federation, role-based access, dual-control approvals, TLS, CSRF protection, rate limits, encrypted storage, migrations, backups and disaster recovery.")
d.bullet("Place signing keys in HSM/KMS; publish signed trust lists and current revocation/status services; anchor audit heads externally.")
d.h2("Phase D — Citizen-scale visualization")
d.bullet("Move to CesiumJS or MapLibre with 3D Tiles for city-scale streaming, level-of-detail, terrain alignment and accessible mobile interactions.")
d.bullet("Provide multilingual UX, assisted workflows, grievance/correction processes and privacy-preserving authenticated access to personal records.")
d.h2("Phase E — Governance and standards")
d.bullet("Define identifier versioning and migration, schema governance, retention, lawful authority, evidence rules, service-level objectives and independent security/privacy assessment.")
d.callout("Recommended next milestone", "Build one authoritative-pilot parcel from a licensed survey/BIM source in a named CRS and height datum, validate it with an independent surveyor, and run the complete authenticated review workflow without administrative waivers.", tone: teal)
d.end()

// Glossary and repository
d.begin("Reference")
d.title("14. Glossary and repository map", subtitle: "Quick reference for project language and implementation locations")
d.h2("Glossary")
let glossary = [
    ("ULPIN", "Existing 14-digit Unique Land Parcel Identification Number supplied by a land record."),
    ("ULPIN-3D", "Experimental child locator proposed by this project; not an official identifier standard."),
    ("Bounds", "[xMin, yMin, xMax, yMax, zMin, zMax] metric coordinates of a rectangular volume."),
    ("Datum", "Reference surface or level from which height/elevation is measured."),
    ("CRS", "Coordinate reference system defining how coordinates relate to the real world."),
    ("LiDAR", "Laser-derived point measurements; represented here by a small synthetic point cloud."),
    ("ES256", "ECDSA P-256 digital signature using SHA-256."),
    ("GeoJSON", "JSON format used here for visualization features and their properties."),
    ("Audit chain", "Ordered events where each hash commits to the previous event and current event fields."),
    ("Waiver", "Recorded administrative approval despite advisory spatial findings; demo-only behavior.")
]
for item in glossary {
    d.text(item.0, x: margin, y: d.y, w: 78, size: 9.5, color: teal, weight: .bold)
    let h = d.text(item.1, x: margin+84, y: d.y, w: 415, size: 9.3, color: ink, leading: 1.3)
    d.y += max(25, h+5)
}
d.h2("Important source locations")
d.code("apps/viewer/                 interactive isometric 3D model\napps/intake/                 manual + point-cloud geometry capture\napps/registrar/              administrative review workflow\napps/reconcile/              consistency findings dashboard\napps/verify/                 signed offline credential verifier\npackages/ulpin3d/codec.py    compact identifier algorithm\npackages/geometry/model.py   rectangular volume math\npackages/reconciliation/     deterministic record checks\npackages/registry/service.py SQLite workflow + audit chain\npackages/verification/       signed payload creation/validation\nscripts/                     data builders and local API server\ntests/                       Python and JavaScript automated tests")
d.callout("Final perspective", "This repository is strongest as an explainable end-to-end prototype: every visible box can be traced back to input, geometry logic, validation, a decision, stored provenance and a verification mechanism.")
d.end()

d.finish()
print(output)
