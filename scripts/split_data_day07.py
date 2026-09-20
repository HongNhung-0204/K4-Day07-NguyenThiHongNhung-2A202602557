from __future__ import annotations

import csv
import re
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Data_Day07 (1).docx"
OUTPUT = ROOT / "data" / "shopee-return-refund"
RETRIEVED_AT = "2026-09-20"

SECTIONS = [
    (0, 70, "return-by-change-of-mind", "Điều kiện trả hàng do đổi ý", "returns-policy", "not-stated"),
    (70, 129, "general-return-refund-rules", "Quy định chung về trả hàng và hoàn tiền", "returns-policy", "https://help.shopee.vn/s/article/Ch%C3%ADnh-s%C3%A1ch-tr%E1%BA%A3-h%C3%A0ng-c%E1%BB%A7a-Shopee-l%C3%A0-g%C3%AC-1542942384513"),
    (129, 138, "restricted-return-products", "Sản phẩm hạn chế trả hàng", "product-restrictions", "https://help.shopee.vn/portal/4/article/79465"),
    (138, 201, "return-refund-evidence", "Bằng chứng khi yêu cầu trả hàng và hoàn tiền", "evidence", "https://help.shopee.vn/vn/s/article/Khi-y%C3%AAu-c%E1%BA%A7u-Tr%E1%BA%A3-h%C3%A0ng-Ho%C3%A0n-ti%E1%BB%81n-ng%C6%B0%E1%BB%9Di-mua-c%E1%BA%A7n-cung-c%E1%BA%A5p-nh%E1%BB%AFng-b%E1%BA%B1ng-ch%E1%BB%A9ng-g%C3%AC"),
    (201, 298, "submit-return-refund-request", "Cách gửi yêu cầu trả hàng và hoàn tiền", "request-process", "https://help.shopee.vn/s/article/lam-the-nao-de-yeu-cau-tra-hang-hoan-tien-cho-san-pham"),
    (298, 332, "track-return-request", "Theo dõi yêu cầu trả hàng", "request-status", "https://help.shopee.vn/s/article/tra-hang-lam-sao-de-kiem-tra-trang-thai-don-hang-hoan-ve-cho-nguoi-ban"),
    (332, 413, "review-return-request", "Shopee xem xét yêu cầu trả hàng", "review-process", "https://help.shopee.vn/s/article/shopee-se-xu-ly-yeu-cau-tra-hang-hoan-tien-cua-toi-nhu-the-nao"),
    (413, 593, "return-shipping-packaging-fees", "Đóng gói, gửi trả hàng và phí trả hàng", "return-shipping", "https://help.shopee.vn/s/article/H%C6%B0%E1%BB%9Bng-d%E1%BA%ABn-tr%E1%BA%A3-h%C3%A0ng-d%C3%A0nh-cho-Ng%C6%B0%E1%BB%9Di-mua"),
    (593, 620, "seller-refund-dispute", "Người bán khiếu nại hoàn tiền", "seller-process", "https://help.shopee.vn/s/article/nguoi-ban-se-lam-gi-sau-khi-nhan-duoc-yeu-cau-cua-toi"),
    (620, 681, "refund-timing-and-methods", "Thời gian và phương thức hoàn tiền", "refund-process", "https://help.shopee.vn/s/article/Sau-khi-g%E1%BB%ADi-y%C3%AAu-c%E1%BA%A7u-tr%E1%BA%A3-h%C3%A0ng-trong-bao-l%C3%A2u-t%C3%B4i-s%E1%BA%BD-nh%E1%BA%ADn-%C4%91%C6%B0%E1%BB%A3c-ti%E1%BB%81n-ho%C3%A0n-tr%E1%BA%A3-1542942531227"),
]


def iter_blocks(document: DocumentObject):
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def table_markdown(table: Table) -> str:
    rows = [[clean(cell.text) for cell in row.cells] for row in table.rows]
    rows = [row for row in rows if any(row)]
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join(["---"] * width) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join(lines)


def main() -> None:
    document = Document(SOURCE)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for old_file in OUTPUT.glob("*.md"):
        old_file.unlink()
    section_contents = {doc_id: [] for _, _, doc_id, _, _, _ in SECTIONS}
    paragraph_index = -1
    current = None

    for block in iter_blocks(document):
        if isinstance(block, Paragraph):
            paragraph_index += 1
            current = next(
                (doc_id for start, end, doc_id, _, _, _ in SECTIONS if start <= paragraph_index < end),
                current,
            )
            text = clean(block.text)
            if not text or current is None:
                continue
            if block.style.name.lower().startswith("heading") or block.style.name in {"Title", "Subtitle"}:
                section_contents[current].append(f"## {text}")
            else:
                section_contents[current].append(text)
        elif isinstance(block, Table) and current is not None:
            rendered = table_markdown(block)
            if rendered:
                section_contents[current].append(rendered)

    rows = []
    for _, _, doc_id, title, category, source_url in SECTIONS:
        content = "\n\n".join(section_contents[doc_id]).strip()
        front_matter = "\n".join(
            [
                "---",
                f"doc_id: {doc_id}",
                f"title: {title}",
                f"source_url: {source_url}",
                f"retrieved_at: {RETRIEVED_AT}",
                'document_version: "not-stated"',
                "audience: buyer",
                f"category: {category}",
                "language: vi",
                "---",
            ]
        )
        (OUTPUT / f"{doc_id}.md").write_text(f"{front_matter}\n\n{content}\n", encoding="utf-8")
        rows.append(
            {
                "doc_id": doc_id,
                "file_path": f"data/shopee-return-refund/{doc_id}.md",
                "title": title,
                "source_url": source_url,
                "retrieved_at": RETRIEVED_AT,
                "document_version": "not-stated",
                "license_or_permission": "source-and-permission-to-verify",
            }
        )

    with (OUTPUT / "sources.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {len(rows)} Markdown documents in {OUTPUT}")


if __name__ == "__main__":
    main()