function(doc) {
  if (doc.category == 'review') {
  	emit([doc.checksum, doc.category_sub], doc);
  }
}