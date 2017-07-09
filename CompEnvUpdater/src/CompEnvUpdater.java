import java.io.File;
import java.io.FileOutputStream;
import java.util.HashSet;
import java.util.Scanner;

import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.RDFXMLDocumentFormat;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassAssertionAxiom;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLEquivalentClassesAxiom;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectOneOf;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;

import uk.ac.manchester.cs.owl.owlapi.OWLObjectOneOfImpl;


public class CompEnvUpdater {
	
	private static String NS = "http://dase.cs.wright.edu/ontologies/ComputationalEnvironment#";
	private static String dataDir = "data";

	
	public static void main(String[] args) throws Exception {
		
		OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
		OWLDataFactory df = OWLManager.getOWLDataFactory();
		
		// read in the base ontology (ComputationalEnvironment_base.owl)
		File ontologyFile = new File(dataDir, "ComputationalEnvironment.rdf");
		IRI iri = IRI.create(ontologyFile);
		OWLOntology ont = manager.loadOntologyFromOntologyDocument(iri);
		
		// process the files for the controlled vocabularies
		addVocabulary(new File(dataDir, "architectures.txt"), "ProcessorArchitecture", ont, manager, df);
		addVocabulary(new File(dataDir, "distros.txt"), "Distribution", ont, manager, df);
		addVocabulary(new File(dataDir, "kernels.txt"), "Kernel", ont, manager, df);
		addVocabulary(new File(dataDir, "processors.txt"), "ProcessorType", ont, manager, df);
		
		// write out the ontology file (ComputationalEnvironment.owl)
		FileOutputStream out = new FileOutputStream(ontologyFile);
		manager.saveOntology(ont, new RDFXMLDocumentFormat(), out);

		System.out.println("Done!");
	}
	
	
	private static String clean(String s) {
		String term = s.trim();
		term = term.replaceAll(" ", "_");
		term = term.replaceAll("[\\+]", "");
		term = term.replaceAll("/", "-");
		term = term.replaceAll("\"", "");
		term = term.replaceAll("&", "_and_");
		return term;
	}
	
	
	private static void addVocabulary(File file, String cls, OWLOntology ont, 
			OWLOntologyManager manager, OWLDataFactory df) throws Exception {
		
		// read in the vocabulary file and generate OWL axioms for...
		OWLClass tClass = df.getOWLClass(IRI.create(NS + cls));
		HashSet<OWLIndividual> individuals = new HashSet<>();
		Scanner in = new Scanner(file);
		
		while (in.hasNext()) {
			// the item is a NamedIndividual of type cls
			String item = in.nextLine().trim();
			OWLNamedIndividual individual = df.getOWLNamedIndividual(NS + clean(item));
			individuals.add(individual);
		    OWLClassAssertionAxiom classAssertion = df.getOWLClassAssertionAxiom(tClass, individual);
		    manager.addAxiom(ont, classAssertion);
		}
		in.close();
		
		// for all items, generate an OWL axiom that
		// the class is Equivalent to OneOf the NamedIndividuals
		OWLObjectOneOf oneOfExpr = new OWLObjectOneOfImpl(individuals.stream());
		OWLEquivalentClassesAxiom equivClasses = df.getOWLEquivalentClassesAxiom(tClass, oneOfExpr);
		manager.addAxiom(ont, equivClasses);
	}
}
