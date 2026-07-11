package com.project.ocr;

import jakarta.persistence.Entity;

/**
 * @author urvvy1
 * Document: receipt
 */
@Entity
public class Receipt extends Document {
    private String store;
    private String date;
    private String paymentMethod;
    private String total;

    /**
     * Constructor for the database
     */
    public Receipt() {}

    /**
     * Constructor
     * @param store the store
     * @param date the date of the receipt issuance
     * @param paymentMethod the payment method - cash or card
     * @param total the sum of paid money
     */
    public Receipt(String store, String date, String paymentMethod, String total) {
        this.store = store; this.date = date; this.paymentMethod = paymentMethod; this.total = total;
    }

    // Getters

    public String getStore() {
        return store;
    }

    public String getDate() {
        return date;
    }

    public String getPaymentMethod() {
        return paymentMethod;
    }

    public String getTotal() {
        return total;
    }

    // Setters

    public void setStore(String store) {
        this.store = store;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public void setPaymentMethod(String paymentMethod) {
        this.paymentMethod = paymentMethod;
    }

    public void setTotal(String total) {
        this.total = total;
    }
}
