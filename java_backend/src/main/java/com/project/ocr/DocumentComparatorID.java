package com.project.ocr;

import java.util.Comparator;

public class DocumentComparatorID implements Comparator<Document> {
    @Override
    public int compare(Document d1, Document d2) {
        return Long.compare(d1.getId(), d2.getId());
    }
}
