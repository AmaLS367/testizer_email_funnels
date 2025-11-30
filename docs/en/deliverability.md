# Testizer email funnels · Email deliverability guide

This document describes basic settings and practices for good email deliverability from Brevo for the Testizer project.

## 1. Domains and Technical Records

For stable delivery, the sender domain must be configured correctly.

### 1.1. Separate Domain or Subdomain

It is recommended to use a separate domain or subdomain such as:

- `mail.testizer.org`

- `news.testizer.org`

The main idea is not to send mass emails from the same domain where the main website lives, without control.

### 1.2. SPF

The domain DNS must have an SPF record that explicitly allows Brevo servers to send emails on behalf of the domain.

Example:

```text
v=spf1 include:spf.brevo.com ~all
```

It's important not to create multiple SPF records. If a record already exists, add `include:spf.brevo.com` to it.

### 1.3. DKIM

In the Brevo dashboard, you need to:

1. Verify the sender domain.
2. Copy the DKIM records that Brevo provides.
3. Add them to the domain DNS.
4. Wait for Brevo to confirm that the records are correct.

DKIM signs emails, which increases trust from email services.

### 1.4. Custom Tracking Domain

If possible, configure a separate tracking domain in Brevo so that links in emails are of the form:

* `https://click.testizer.org/...`

instead of Brevo domains. This reduces the likelihood of spam and makes links more trustworthy.

## 2. Sender and Headers

### 2.1. Sender Address

Recommended format:

* From: `"Testizer"` or `"Testizer Language Center"`
* Email: `info@testizer.org` or `support@testizer.org`

It's important to use the same sender address for regular emails to build reputation.

### 2.2. Email Subject

Recommendations:

* Clearly describe the email content, without clickbait phrases.
* Don't abuse CAPS LOCK and excessive `!` signs.
* Avoid template spam phrases like "urgent", "only today", "100% guarantee", etc.

## 3. Database Quality and Consent

### 3.1. Database Sources

Only contacts that:

* took the test themselves and provided an email;
* agreed to receive emails.

should enter the database.

You cannot load purchased or "scraped" databases.

### 3.2. Unsubscribes and Complaints

Every email must have:

* a correct unsubscribe link;
* clear text explaining why the person is receiving the email.

It's important to regularly check statistics in Brevo:

* complaint rate;
* unsubscribe rate;
* undelivered email rate (bounces).

If metrics worsen, reduce sending volume and clean the database.

### 3.3. Database Cleaning

Recommended steps:

* periodically remove addresses that don't open emails for a long time;
* work with "cold" segments separately, reducing sending frequency.

## 4. Email Content

### 4.1. Text and Link Balance

Good practice:

* email contains clear text, not just one large button;
* links lead to relevant pages;
* email doesn't have "strange" redirects.

### 4.2. Images

Recommendations:

* don't build emails from one large image;
* always add alt text to images;
* check image weight so emails load quickly.

### 4.3. Localization

For Testizer, it's important:

* to use the correct language for the target audience;
* not to mix too many languages in one email.

## 5. Sending Rate and Warm-up

If email volume will increase:

1. Start with smaller batches.
2. Monitor open and complaint rates.
3. Gradually increase sending volume if statistics are normal.

A sudden increase in email volume without warm-up can lead to blocks.

## 6. Monitoring in Brevo

Important reports to track:

* Delivery rate (percentage of delivered emails).
* Open rate (percentage of opens).
* Click rate (percentage of clicks).
* Complaints.
* Unsubscribes.

If metrics drop, you need to:

* check changes in email content;
* reduce sending frequency;
* review database segmentation.

