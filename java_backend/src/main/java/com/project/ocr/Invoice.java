package com.project.ocr;

import jakarta.persistence.Entity;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

/**
 * @author urvvy1
 * Document: invoice
 */

@Entity
public class Invoice extends Document {
    // attributes may be extended
    private String invoiceNumber;
    private String invoiceDate;
    private String dueDate;
    private String seller;
    private String customer;
    private String description;
    private Map<String, Map<String, String>> goods; //<Name, Map<Amount, Price per one piece>>
    private String totalPrice;
    private String paymentMethod;
    private String bank;

    public Invoice() {};

    public Invoice(String invoiceNumber, String invoiceDate, String dueDate,
                   String seller, String customer, String description, Map<String, Map<String, String>> goods,
                   String totalPrice, String paymentMethod, String bank) {
        this.invoiceNumber = invoiceNumber; this.invoiceDate = invoiceDate; this.dueDate = dueDate;
        this.seller = seller; this.customer = customer; this.description = description;
        this.goods = new HashMap<>();
        this.totalPrice = totalPrice; this.paymentMethod = paymentMethod; this.bank = bank;
    }

    // Getters

    public String getInvoiceNumber() {
        return invoiceNumber;
    }

    public String getInvoiceDate() {
        return invoiceDate;
    }

    public String getDueDate() {
        return dueDate;
    }

    public String getSeller() {
        return seller;
    }

    public String getCustomer() {
        return customer;
    }

    public String getDescription() {
        return description;
    }

    public Map<String, Map<String, String>> getGoods() {
        return Collections.unmodifiableMap(goods);
    }

    public String getTotalPrice() {
        return totalPrice;
    }

    public String getPaymentMethod() {
        return paymentMethod;
    }

    public String getBank() {
        return bank;
    }

    // Setters
    
    public void setInvoiceNumber(String invoiceNumber) {
        this.invoiceNumber = invoiceNumber;
    }

    public void setInvoiceDate(String invoiceDate) {
        this.invoiceDate = invoiceDate;
    }

    public void setDueDate(String dueDate) {
        this.dueDate = dueDate;
    }

    public void setSeller(String seller) {
        this.seller = seller;
    }

    public void setCustomer(String customer) {
        this.customer = customer;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public void setGoods(Map<String, Map<String, String>> goods) {
        this.goods = goods;
    }

    public void setTotalPrice(String totalPrice) {
        this.totalPrice = totalPrice;
    }

    public void setPaymentMethod(String paymentMethod) {
        this.paymentMethod = paymentMethod;
    }

    public void setBank(String bank) {
        this.bank = bank;
    }
}
