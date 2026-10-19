import io
import random
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua enim ad minim veniam quis nostrud "
    "exercitation ullamco laboris nisi aliquip ex ea commodo consequat duis aute irure "
    "in reprehenderit voluptate velit esse cillum fugiat nulla pariatur excepteur sint "
    "occaecat cupidatat non proident sunt culpa qui officia deserunt mollit anim id est "
    "laborum curabitur pretium tincidunt lacus nunc pulvinar sapien ligula vitae "
    "fringilla mauris viverra maecenas accumsan faucibus vestibulum ante primis "
    "ultrices posuere cubilia curae praesent blandit odio quam pellentesque habitant "
    "morbi tristique senectus netus malesuada fames ac turpis egestas integer feugiat "
    "scelerisque varius porttitor rhoncus dignissim convallis aenean"
).split()

COVER = Path(__file__).with_name("cover.jpg")
TITLE = "Lorem Ipsum"
SERIES = "Lorem Ipsum"
TARGET_BYTES = 500_000


def sentence(rng):
    words = [rng.choice(WORDS) for _ in range(rng.randint(8, 22))]
    words[0] = words[0].capitalize()
    for i in range(1, len(words) - 1):
        if rng.random() < 0.08:
            words[i] += ","
    return " ".join(words) + "."


def paragraph(rng):
    return " ".join(sentence(rng) for _ in range(rng.randint(3, 8)))


def chapter_xhtml(number, rng):
    paragraphs = "\n".join(f"    <p>{paragraph(rng)}</p>" for _ in range(rng.randint(25, 40)))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="la" xml:lang="la">
<head>
  <title>Chapter {number}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <section epub:type="chapter">
    <h1>Chapter {number}</h1>
{paragraphs}
  </section>
</body>
</html>
"""


def nav_xhtml(count):
    items = "\n".join(
        f'      <li><a href="chapter{n:03d}.xhtml">Chapter {n}</a></li>' for n in range(1, count + 1)
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><title>Contents</title></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Contents</h1>
    <ol>
{items}
    </ol>
  </nav>
</body>
</html>
"""


def toc_ncx(book_id, count):
    points = "\n".join(
        f"""    <navPoint id="np{n}" playOrder="{n}">
      <navLabel><text>Chapter {n}</text></navLabel>
      <content src="chapter{n:03d}.xhtml"/>
    </navPoint>"""
        for n in range(1, count + 1)
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{book_id}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{TITLE}</text></docTitle>
  <navMap>
{points}
  </navMap>
</ncx>
"""


def content_opf(book_id, count):
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = "\n".join(
        f'    <item id="ch{n:03d}" href="chapter{n:03d}.xhtml" media-type="application/xhtml+xml"/>'
        for n in range(1, count + 1)
    )
    spine = "\n".join(f'    <itemref idref="ch{n:03d}"/>' for n in range(1, count + 1))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="bookid">urn:uuid:{book_id}</dc:identifier>
    <dc:title>{TITLE}</dc:title>
    <dc:creator>Test Generator</dc:creator>
    <dc:language>la</dc:language>
    <meta property="dcterms:modified">{modified}</meta>
    <meta name="calibre:series" content="{SERIES}"/>
    <meta name="calibre:series_index" content="1"/>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    <item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>
    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
{manifest}
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover"/>
{spine}
  </spine>
</package>
"""


COVER_XHTML = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head>
  <title>Cover</title>
  <style>body {{ margin: 0; padding: 0; text-align: center; }} img {{ max-width: 100%; max-height: 100%; }}</style>
</head>
<body>
  <section epub:type="cover">
    <img src="cover.jpg" alt="{TITLE}"/>
  </section>
</body>
</html>
"""

CONTAINER = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

STYLE = "body { margin: 0; }\nh1 { text-align: center; }\np { text-indent: 1.5em; margin: 0 0 0.5em 0; }\n"


def build(count, seed=42):
    rng = random.Random(seed)
    book_id = uuid.UUID(int=random.Random(seed).getrandbits(128))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        deflate = dict(compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        z.writestr("META-INF/container.xml", CONTAINER, **deflate)
        z.writestr("OEBPS/content.opf", content_opf(book_id, count), **deflate)
        z.writestr("OEBPS/nav.xhtml", nav_xhtml(count), **deflate)
        z.writestr("OEBPS/toc.ncx", toc_ncx(book_id, count), **deflate)
        z.writestr("OEBPS/style.css", STYLE, **deflate)
        z.writestr("OEBPS/cover.xhtml", COVER_XHTML, **deflate)
        z.writestr("OEBPS/cover.jpg", COVER.read_bytes(), compress_type=zipfile.ZIP_STORED)
        for n in range(1, count + 1):
            z.writestr(f"OEBPS/chapter{n:03d}.xhtml", chapter_xhtml(n, rng), **deflate)
    return buf.getvalue()


def main():
    out = Path(sys.argv[1])
    sample = 10
    count = max(1, TARGET_BYTES * sample // len(build(sample)))
    data = build(count)
    while len(data) > TARGET_BYTES and count > 1:
        count -= 1
        data = build(count)
    while len(data) < TARGET_BYTES:
        count += 1
        data = build(count)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"{out} chapters={count} bytes={len(data):,}")


if __name__ == "__main__":
    main()
