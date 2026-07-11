package com.project.ocr;

import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.MappedSuperclass;

/**
 * @author urvv1y
 * Abstract class for defining a document.
 */

@MappedSuperclass
public abstract class Document {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    public Document() {
    }

    public Long getId() {
        return id;
    }

    public void setId() {
        this.id = id;
    }
}
